#!/usr/bin/env python3
"""
Add LLM-based psychological analysis to existing conversation files.
This script processes all conversation JSON files and adds LLM analysis data.
"""

import os
# Disable tokenizer parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import json
import time
from pathlib import Path
from tqdm import tqdm

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Ensure we're using the venv
venv_python = Path(__file__).parent / "venv" / "bin" / "python"
if not str(sys.executable).startswith(str(venv_python.parent)):
    print(f"⚠️  Please run this script with: source venv/bin/activate && python {__file__}")
    print(f"   Or: ./venv/bin/python {__file__}")
    sys.exit(1)

from llm_analyzer import LLMAnalyzer
from llm_monitor import get_monitor
from create_llm_dashboard import create_llm_performance_dashboard

# Configuration
CONVERSATIONS_DIR = Path(__file__).parent / "data" / "output" / "all_conversations"
CHUNK_SIZE = 15  # Number of messages per chunk (typically ~1500-2000 chars with context)
OVERLAP = 5  # Number of messages to overlap between chunks (maintains continuity)
MIN_MESSAGES = 20  # Only analyze conversations with at least this many messages
MAX_CONVERSATIONS = 5  # Set to None to process all, or a number to limit (e.g., 5 for testing)

def main():
    """Add LLM analysis to all conversation files."""

    print("=" * 80)
    print("ADDING LLM ANALYSIS TO ALL CONVERSATIONS")
    print("=" * 80)
    print()

    # Initialize analyzer
    print("Initializing LLM analyzer...")
    analyzer = LLMAnalyzer(use_gpu=True)
    monitor = get_monitor()

    # Find all conversation files (non-analysis files), sorted by message count (descending)
    all_files = [
        f for f in CONVERSATIONS_DIR.glob("*.json")
        if not f.name.endswith("_analysis.json") and not f.name.endswith("_llm_analysis.json")
    ]

    # Sort by message count (extract from filename: XXXX_NNNN_msgs_...)
    # Filter out files that don't match the expected pattern
    valid_files = []
    for f in all_files:
        parts = f.name.split('_')
        if len(parts) >= 2:
            try:
                msg_count = int(parts[1])
                valid_files.append((msg_count, f))
            except ValueError:
                # Skip files with non-numeric message counts (like MASTER_dashboard.json)
                continue

    # Sort by message count ASCENDING (smallest first for quick results)
    conversation_files = [f for _, f in sorted(valid_files, key=lambda x: x[0], reverse=False)]

    # Limit to first N if specified
    if MAX_CONVERSATIONS:
        conversation_files = conversation_files[:MAX_CONVERSATIONS]
        print(f"\n🎯 Processing first {MAX_CONVERSATIONS} conversations (smallest first for quick results)")

    # Calculate total messages and chunks
    total_messages = 0
    total_chunks = 0
    for f in conversation_files:
        msg_count = int(f.name.split('_')[1])
        total_messages += msg_count
        # Estimate chunks: roughly (messages / (chunk_size - overlap))
        chunks_per_conv = max(1, msg_count // (CHUNK_SIZE - OVERLAP))
        total_chunks += chunks_per_conv

    # Estimate time (rough: ~0.5s per chunk for 4 model inferences)
    estimated_seconds = total_chunks * 0.5
    estimated_minutes = estimated_seconds / 60

    print(f"\nFound {len(conversation_files)} conversation files to process")
    print(f"Total messages: {total_messages:,}")
    print(f"Estimated chunks (with overlap): {total_chunks:,}")
    print(f"Chunk size: {CHUNK_SIZE} messages, Overlap: {OVERLAP} messages")
    print(f"Estimated time: {estimated_minutes:.1f} minutes")
    print(f"Minimum messages per conversation: {MIN_MESSAGES}")
    print()

    # Process each conversation
    processed = 0
    skipped = 0
    start_time = time.time()
    messages_processed = 0

    for idx, conv_file in enumerate(tqdm(conversation_files, desc="Processing conversations"), 1):
        try:
            # Load conversation
            with open(conv_file, 'r') as f:
                data = json.load(f)

            # Check if it has enough messages
            messages = data.get('messages', [])
            if len(messages) < MIN_MESSAGES:
                skipped += 1
                continue

            # Check if analysis already exists
            analysis_file = conv_file.parent / f"{conv_file.stem}_llm_analysis.json"
            if analysis_file.exists():
                tqdm.write(f"  ✓ Skipping {conv_file.name} (already analyzed)")
                continue

            conv_start = time.time()
            tqdm.write(f"\n  Analyzing {conv_file.name} ({len(messages)} messages)...")

            # Run LLM analysis with chunking and GPU batching
            llm_results = analyzer.analyze_conversation(messages, chunk_size=CHUNK_SIZE, overlap=OVERLAP, batch_size=16)
            chunks_analyzed = llm_results['metadata'].get('chunks_analyzed', 0)
            messages_processed += chunks_analyzed

            # Create output file with LLM analysis
            output_data = {
                'conversation_file': conv_file.name,
                'conversation_name': data.get('conversation_name'),
                'total_messages': len(messages),
                'llm_analysis': llm_results,
                'analysis_config': {
                    'chunk_size': CHUNK_SIZE,
                    'overlap': OVERLAP,
                    'models_used': [
                        'holistic-ai/personality_classifier',
                        'martin-ha/toxic-comment-model',
                        'jkhan447/sarcasm-detection-RoBerta-base',
                        'finiteautomata/bertweet-base-sentiment-analysis'
                    ]
                }
            }

            # Save LLM analysis
            with open(analysis_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            conv_time = time.time() - conv_start
            processed += 1

            # Calculate progress stats
            elapsed_time = time.time() - start_time
            avg_time_per_chunk = elapsed_time / messages_processed if messages_processed > 0 else 0
            remaining_chunks = total_chunks - messages_processed
            estimated_remaining = remaining_chunks * avg_time_per_chunk / 60

            tqdm.write(f"  ✓ Saved to {analysis_file.name} ({conv_time:.1f}s, {chunks_analyzed} chunks)")
            tqdm.write(f"  📊 Progress: {messages_processed:,}/{total_chunks:,} chunks | ~{estimated_remaining:.1f} min remaining")

        except Exception as e:
            tqdm.write(f"  ✗ Error processing {conv_file.name}: {e}")
            continue

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Processed: {processed} conversations")
    print(f"Skipped: {skipped} (too few messages)")
    print()

    # Print performance summary
    monitor.print_summary()

    # Save metrics
    print("Saving performance metrics...")
    metrics_file = monitor.save_metrics('llm_conversation_analysis_metrics.json')
    print(f"✓ Metrics saved to: {metrics_file}")

    # Generate dashboard
    print("\nGenerating performance dashboard...")
    dashboard_file = create_llm_performance_dashboard(metrics_file)
    print(f"✓ Dashboard created: {dashboard_file}")
    print(f"\n📊 Open the dashboard in your browser:")
    print(f"   file://{dashboard_file.absolute()}")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Review the performance dashboard to check model efficiency")
    print("2. Run 'python src/generate_master_dashboard.py' to update master dashboard")
    print("3. LLM analysis results are saved as *_llm_analysis.json files")
    print()


if __name__ == "__main__":
    main()

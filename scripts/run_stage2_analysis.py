#!/usr/bin/env python3
"""
Stage 2: Dual LLM Cumulative Analysis

Runs Llama 3.2-8B and Qwen 2.5-7B on conversations that have completed Stage 1 analysis.
Uses large chunks (8000 tokens) to provide maximum context to the models.

Context windows:
- Llama 3.2: 131,072 tokens (128K)
- Qwen 2.5: 32,768 tokens (32K)
"""

import sys
import json
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from stage2_llm_analyzer import Stage2LLMAnalyzer


def main(conversation_file: str = None, chunk_size: int = 8000, overlap: int = 800):
    """
    Run Stage 2 analysis on a conversation with existing Stage 1 results.

    Args:
        conversation_file: Path to conversation JSON file (if None, uses smallest with Stage 1 data)
        chunk_size: Tokens per chunk (default: 8000 - works well with both models' large context windows)
        overlap: Token overlap (default: 800 - 10% overlap)
    """
    print("=" * 80)
    print("STAGE 2: DUAL LLM CUMULATIVE ANALYSIS")
    print("=" * 80)
    print()
    print("Models: Llama 3.2-8B (128K context) + Qwen 2.5-7B (32K context)")
    print(f"Chunk size: {chunk_size:,} tokens, Overlap: {overlap:,} tokens")
    print()

    # Find conversation file
    conversations_dir = Path(__file__).parent / "data" / "output" / "all_conversations"

    if conversation_file is None:
        # Find conversations with Stage 1 analysis
        llm_analysis_files = list(conversations_dir.glob("*_llm_analysis.json"))

        if not llm_analysis_files:
            print("❌ No Stage 1 analysis files found (*_llm_analysis.json)")
            print("   Please run Stage 1 first using add_llm_analysis.py")
            return

        # Use smallest conversation for testing
        llm_analysis_files.sort(key=lambda f: int(f.name.split('_')[1]))
        stage1_file = llm_analysis_files[0]

        # Find corresponding conversation file
        conv_name = stage1_file.name.replace('_llm_analysis.json', '.json')
        conversation_file = conversations_dir / conv_name

        print(f"Using test conversation: {conversation_file.name}")
        print(f"With Stage 1 analysis: {stage1_file.name}\n")
    else:
        conversation_file = Path(conversation_file)
        stage1_file = conversation_file.parent / f"{conversation_file.stem}_llm_analysis.json"

        if not stage1_file.exists():
            print(f"❌ Stage 1 analysis not found: {stage1_file.name}")
            print("   Please run Stage 1 first using add_llm_analysis.py")
            return

    # Load conversation
    print(f"Loading conversation...")
    with open(conversation_file, 'r') as f:
        conv_data = json.load(f)

    messages = conv_data.get('messages', [])
    conv_name = conv_data.get('conversation_name', 'unknown')

    # Load Stage 1 analysis
    print(f"Loading Stage 1 analysis...")
    with open(stage1_file, 'r') as f:
        stage1_data = json.load(f)

    stage1_results = stage1_data.get('llm_analysis', {})

    print(f"\nConversation: {conv_name}")
    print(f"Total messages: {len(messages)}")
    print(f"Stage 1 chunks analyzed: {stage1_results.get('metadata', {}).get('chunks_analyzed', 'unknown')}\n")

    # Check if Stage 2 already exists
    llama_file = conversation_file.parent / f"{conversation_file.stem}_stage2_llama3.2.json"
    qwen_file = conversation_file.parent / f"{conversation_file.stem}_stage2_qwen2.5_7b-instruct.json"

    if llama_file.exists() and qwen_file.exists():
        print(f"⚠️  Stage 2 analysis already exists:")
        print(f"   - {llama_file.name}")
        print(f"   - {qwen_file.name}")
        response = input("\nOverwrite existing analysis? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
        print()

    # ========== STAGE 2: DUAL LLM ANALYSIS ==========
    print("=" * 80)
    print("RUNNING STAGE 2 ANALYSIS")
    print("=" * 80)
    print()

    stage2_start = time.time()

    # Initialize Stage 2 analyzer
    print("Initializing Llama 3.2-8B and Qwen 2.5-7B via Ollama...")
    stage2_analyzer = Stage2LLMAnalyzer(models=['llama3.2', 'qwen2.5:7b-instruct'])

    # Run Stage 2 analysis
    stage2_results = stage2_analyzer.analyze_conversation(
        messages=messages,
        stage1_results=stage1_results,
        chunk_size=chunk_size,
        overlap=overlap
    )

    stage2_elapsed = time.time() - stage2_start

    # ========== SAVE RESULTS ==========
    print(f"\n{'=' * 80}")
    print("SAVING RESULTS")
    print("=" * 80)
    print()

    # Save Stage 2 results (one file per model)
    for model_name, analyses in stage2_results.items():
        # Sanitize model name for filename
        safe_model_name = model_name.replace(':', '_').replace('/', '_')
        stage2_file = conversation_file.parent / f"{conversation_file.stem}_stage2_{safe_model_name}.json"

        output_data = {
            'conversation_file': conversation_file.name,
            'conversation_name': conv_name,
            'total_messages': len(messages),
            'model': model_name,
            'chunk_analyses': analyses,
            'config': {
                'chunk_size': chunk_size,
                'overlap': overlap,
                'context_window': '131072 tokens' if 'llama' in model_name else '32768 tokens'
            },
            'stage1_reference': stage1_file.name
        }

        with open(stage2_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"✓ {model_name}: {stage2_file.name}")
        print(f"  - {len(analyses)} chunks analyzed")

        # Show sample of first chunk
        if analyses:
            first_chunk = analyses[0]
            print(f"  - First chunk summary: {first_chunk.get('cumulative_summary', 'N/A')[:100]}...")

        print()

    # ========== SUMMARY ==========
    print("=" * 80)
    print("STAGE 2 COMPLETE")
    print("=" * 80)
    print(f"\nConversation: {conv_name}")
    print(f"Total messages: {len(messages)}")
    print(f"Chunks per model: {len(stage2_results['llama3.2'])}")
    print(f"Total time: {stage2_elapsed:.1f}s")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Stage 2 (Dual LLM) analysis on a conversation")
    parser.add_argument("--file", type=str, default=None, help="Conversation JSON file (if not specified, uses smallest with Stage 1)")
    parser.add_argument("--chunk-size", type=int, default=8000, help="Tokens per chunk (default: 8000)")
    parser.add_argument("--overlap", type=int, default=800, help="Token overlap (default: 800)")

    args = parser.parse_args()

    main(conversation_file=args.file, chunk_size=args.chunk_size, overlap=args.overlap)

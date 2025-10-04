#!/usr/bin/env python3
"""
Run Stage 1 analysis on a single conversation.
"""

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm_analyzer import LLMAnalyzer
from llm_monitor import get_monitor


def main(phone_number: str):
    """Run Stage 1 analysis on a specific conversation."""

    conversations_dir = Path(__file__).parent / "data" / "output" / "all_conversations"

    # Find conversation file
    matches = list(conversations_dir.glob(f"*{phone_number}*.json"))
    matches = [f for f in matches if not f.name.endswith("_analysis.json") and not f.name.endswith("_llm_analysis.json")]

    if not matches:
        print(f"❌ No conversation found for {phone_number}")
        return

    # Use the one with most messages
    matches.sort(key=lambda f: int(f.name.split('_')[1]), reverse=True)
    conv_file = matches[0]

    print("=" * 80)
    print(f"STAGE 1: ANALYZING {conv_file.name}")
    print("=" * 80)
    print()

    # Load conversation
    with open(conv_file, 'r') as f:
        data = json.load(f)

    messages = data.get('messages', [])
    conv_name = data.get('conversation_name')

    print(f"Conversation: {conv_name}")
    print(f"Total messages: {len(messages)}\n")

    # Check if already analyzed
    analysis_file = conv_file.parent / f"{conv_file.stem}_llm_analysis.json"
    if analysis_file.exists():
        print(f"⚠️  Analysis already exists: {analysis_file.name}")
        response = input("Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
        print()

    # Initialize analyzer
    print("Loading LLM models (using CPU to avoid MPS issues)...")
    analyzer = LLMAnalyzer(use_gpu=False)
    monitor = get_monitor()

    # Run analysis
    print(f"\nAnalyzing conversation with chunk_size=15, overlap=5...")
    start_time = time.time()

    llm_results = analyzer.analyze_conversation(messages, chunk_size=15, overlap=5, batch_size=16)

    elapsed = time.time() - start_time

    # Save results
    output_data = {
        'conversation_file': conv_file.name,
        'conversation_name': conv_name,
        'total_messages': len(messages),
        'llm_analysis': llm_results,
        'analysis_config': {
            'chunk_size': 15,
            'overlap': 5,
            'models_used': [
                'holistic-ai/personality_classifier',
                'martin-ha/toxic-comment-model',
                'jkhan447/sarcasm-detection-RoBerta-base',
                'finiteautomata/bertweet-base-sentiment-analysis'
            ]
        }
    }

    with open(analysis_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✓ Analysis complete in {elapsed:.1f}s")
    print(f"✓ Saved to: {analysis_file.name}\n")

    # Print summary
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    your_analysis = llm_results.get('your_analysis', {})
    their_analysis = llm_results.get('their_analysis', {})

    print("\nYou:")
    if 'toxicity' in your_analysis:
        tox = your_analysis['toxicity']
        print(f"  Toxicity: {tox.get('rate', 0)*100:.1f}% ({tox.get('toxic_messages', 0)}/{tox.get('total_analyzed', 0)} messages)")
    if 'sentiment' in your_analysis:
        sent = your_analysis['sentiment']
        print(f"  Sentiment: POS={sent.get('positive_rate', 0)*100:.1f}%, NEG={sent.get('negative_rate', 0)*100:.1f}%, NEU={sent.get('neutral_rate', 0)*100:.1f}%")

    print("\nThem:")
    if 'toxicity' in their_analysis:
        tox = their_analysis['toxicity']
        print(f"  Toxicity: {tox.get('rate', 0)*100:.1f}% ({tox.get('toxic_messages', 0)}/{tox.get('total_analyzed', 0)} messages)")
    if 'sentiment' in their_analysis:
        sent = their_analysis['sentiment']
        print(f"  Sentiment: POS={sent.get('positive_rate', 0)*100:.1f}%, NEG={sent.get('negative_rate', 0)*100:.1f}%, NEU={sent.get('neutral_rate', 0)*100:.1f}%")

    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_stage1_single.py <phone_number>")
        print("Example: python run_stage1_single.py 309-948-9979")
        sys.exit(1)

    main(sys.argv[1])

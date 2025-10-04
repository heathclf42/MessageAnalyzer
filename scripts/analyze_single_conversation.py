#!/usr/bin/env python3
"""
Analyze a single conversation with LLM models.
"""

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import json
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Check venv
venv_python = Path(__file__).parent / "venv" / "bin" / "python"
if not str(sys.executable).startswith(str(venv_python.parent)):
    print(f"⚠️  Please run: source venv/bin/activate && python {__file__}")
    sys.exit(1)

from llm_analyzer import LLMAnalyzer
from llm_monitor import get_monitor
from create_llm_dashboard import create_llm_performance_dashboard

# Configuration
CONVERSATIONS_DIR = Path(__file__).parent / "data" / "output" / "all_conversations"
CHUNK_SIZE = 15
OVERLAP = 5

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_single_conversation.py <phone_number>")
        print("Example: python analyze_single_conversation.py 817-709-1307")
        sys.exit(1)

    # Normalize phone number (remove all non-digits)
    phone_input = ''.join(c for c in sys.argv[1] if c.isdigit())
    phone = phone_input  # Keep for later use

    # Find the conversation file (search for phone number in any format)
    conv_file = None
    for f in CONVERSATIONS_DIR.glob("*.json"):
        if f.name.endswith("_analysis.json") or f.name.endswith("_llm_analysis.json"):
            continue
        # Extract digits from filename
        filename_digits = ''.join(c for c in f.name if c.isdigit())
        if phone_input in filename_digits:
            conv_file = f
            break

    if not conv_file:
        print(f"❌ Conversation not found for {sys.argv[1]}")
        print(f"   Searched for: {phone_input}")
        print(f"\n   Available conversations (first 10):")
        for i, f in enumerate(sorted(CONVERSATIONS_DIR.glob("*.json"))[:10]):
            if not f.name.endswith("_analysis.json") and not f.name.endswith("_llm_analysis.json"):
                print(f"     {f.name}")
        sys.exit(1)

    print("=" * 80)
    print(f"ANALYZING CONVERSATION: {sys.argv[1]}")
    print("=" * 80)
    print()

    # Load conversation
    with open(conv_file, 'r') as f:
        data = json.load(f)

    messages = data.get('messages', [])
    print(f"Conversation file: {conv_file.name}")
    print(f"Total messages: {len(messages)}")
    print(f"Date range: {data.get('date_range', 'unknown')}")
    print()

    # Estimate time (one set of chunks for the conversation, not per sender)
    chunks_estimate = max(1, len(messages) // (CHUNK_SIZE - OVERLAP))
    time_estimate = chunks_estimate * 0.5 / 60
    print(f"Estimated chunks: {chunks_estimate}")
    print(f"Estimated time: {time_estimate:.1f} minutes")
    print()

    # Initialize analyzer
    print("Initializing LLM analyzer...")
    analyzer = LLMAnalyzer(use_gpu=True)
    monitor = get_monitor()

    # Run analysis with progress tracking
    start_time = time.time()
    print(f"\n{'='*80}")
    print("ANALYSIS IN PROGRESS")
    print(f"{'='*80}\n")

    print(f"Start time: {time.strftime('%H:%M:%S')}")
    print(f"Estimated chunks to process: {chunks_estimate}")
    print(f"Estimated completion: {time_estimate:.1f} minutes\n")

    llm_results = analyzer.analyze_conversation(messages, chunk_size=CHUNK_SIZE, overlap=OVERLAP, batch_size=16)

    analysis_time = time.time() - start_time
    end_time = time.strftime('%H:%M:%S')

    # Save results first (before any potential errors)
    analysis_file = conv_file.parent / f"{conv_file.stem}_llm_analysis.json"
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

    with open(analysis_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n{'='*80}")
    print(f"Start time: {time.strftime('%H:%M:%S', time.localtime(start_time))}")
    print(f"End time: {end_time}")
    print(f"Total wall clock time: {analysis_time/60:.1f} minutes ({analysis_time:.0f} seconds)")
    print(f"{'='*80}\n")

    print(f"✓ Analysis complete")
    print(f"✓ Saved to: {analysis_file.name}")

    # Print results summary
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)

    your_analysis = llm_results.get('your_analysis', {})
    their_analysis = llm_results.get('their_analysis', {})

    print("\n📊 YOUR PROFILE:")
    if your_analysis:
        personality = your_analysis.get('personality', {})
        holistic = personality.get('holistic_ai', {})
        bert = personality.get('bert_base', {})

        print(f"  Personality (holistic-ai): {holistic.get('primary_trait', 'N/A')}")
        if bert.get('big5_scores'):
            print(f"  Personality (bert-base Big 5):")
            for trait, score in bert['big5_scores'].items():
                print(f"    {trait}: {score:.3f}")

        toxicity = your_analysis.get('toxicity', {})
        print(f"  Toxicity (martin-ha): {toxicity.get('martin_ha', {}).get('rate', 0)*100:.1f}%")
        print(f"  Toxicity (toxicchat): {toxicity.get('toxicchat', {}).get('rate', 0)*100:.1f}%")
        print(f"  Toxicity (average): {toxicity.get('average_rate', 0)*100:.1f}%")

        sarcasm = your_analysis.get('sarcasm', {})
        print(f"  Sarcasm Rate: {sarcasm.get('rate', 0)*100:.1f}%")

        sentiment = your_analysis.get('sentiment', {})
        print(f"  Positive: {sentiment.get('positive_rate', 0)*100:.1f}%")
        print(f"  Negative: {sentiment.get('negative_rate', 0)*100:.1f}%")

    print("\n📊 THEIR PROFILE:")
    if their_analysis:
        personality = their_analysis.get('personality', {})
        holistic = personality.get('holistic_ai', {})
        bert = personality.get('bert_base', {})

        print(f"  Personality (holistic-ai): {holistic.get('primary_trait', 'N/A')}")
        if bert.get('big5_scores'):
            print(f"  Personality (bert-base Big 5):")
            for trait, score in bert['big5_scores'].items():
                print(f"    {trait}: {score:.3f}")

        toxicity = their_analysis.get('toxicity', {})
        print(f"  Toxicity (martin-ha): {toxicity.get('martin_ha', {}).get('rate', 0)*100:.1f}%")
        print(f"  Toxicity (toxicchat): {toxicity.get('toxicchat', {}).get('rate', 0)*100:.1f}%")
        print(f"  Toxicity (average): {toxicity.get('average_rate', 0)*100:.1f}%")

        sarcasm = their_analysis.get('sarcasm', {})
        print(f"  Sarcasm Rate: {sarcasm.get('rate', 0)*100:.1f}%")

        sentiment = their_analysis.get('sentiment', {})
        print(f"  Positive: {sentiment.get('positive_rate', 0)*100:.1f}%")
        print(f"  Negative: {sentiment.get('negative_rate', 0)*100:.1f}%")

    # Performance summary
    print("\n" + "=" * 80)
    monitor.print_summary()

    # Save metrics
    metrics_file = monitor.save_metrics(f'llm_analysis_{phone}.json')
    print(f"✓ Metrics saved to: {metrics_file}")

    # Generate dashboard
    dashboard_file = create_llm_performance_dashboard(metrics_file)
    print(f"✓ Dashboard created: {dashboard_file}")
    print(f"\n📊 Open the dashboard: file://{dashboard_file.absolute()}")
    print()

if __name__ == "__main__":
    main()

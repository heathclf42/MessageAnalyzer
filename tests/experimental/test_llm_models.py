#!/usr/bin/env python3
"""
Test script for LLM-based psychological analysis models.
Downloads and tests non-gated specialized models immediately.
Includes performance monitoring and dashboard generation.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Ensure we're using the venv
venv_python = Path(__file__).parent / "venv" / "bin" / "python"
if not str(sys.executable).startswith(str(venv_python.parent)):
    print(f"⚠️  Please run this script with: source venv/bin/activate && python {__file__}")
    print(f"   Or: ./venv/bin/python {__file__}")
    sys.exit(1)

from llm_monitor import LLMMonitor
from create_llm_dashboard import create_llm_performance_dashboard

print("=" * 80)
print("LLM MODEL DOWNLOAD AND TEST WITH PERFORMANCE MONITORING")
print("=" * 80)
print()

# Initialize performance monitor
monitor = LLMMonitor()
print("✓ Performance monitoring initialized\n")

# Test text samples
test_texts = [
    "I'm feeling really great about this project! So excited to see the results.",
    "Whatever. I don't even care anymore. Nothing matters anyway.",
    "I love helping people and making sure everyone feels supported and valued.",
    "The quick brown fox jumps over the lazy dog. This is a neutral test sentence.",
    "You're absolutely terrible at this. Can't believe how incompetent you are.",
]

print("Step 1: Downloading specialized models (this will take a few minutes)...")
print("-" * 80)

try:
    from transformers import pipeline

    # Big 5 Personality (non-gated, available immediately)
    print("\n📥 Downloading personality classifier (~500MB)...")
    personality_model = pipeline("text-classification",
                                model="holistic-ai/personality_classifier",
                                device="mps")  # Use Apple Silicon GPU
    print("✓ Personality model ready")

    # Toxicity detection
    print("\n📥 Downloading toxicity detector (~265MB)...")
    toxicity_model = pipeline("text-classification",
                             model="martin-ha/toxic-comment-model",
                             device="mps")
    print("✓ Toxicity model ready")

    # Sarcasm detection
    print("\n📥 Downloading sarcasm detector (~500MB)...")
    sarcasm_model = pipeline("text-classification",
                            model="jkhan447/sarcasm-detection-RoBerta-base",
                            device="mps")
    print("✓ Sarcasm model ready")

    # Sentiment analysis
    print("\n📥 Downloading sentiment analyzer (~500MB)...")
    sentiment_model = pipeline("sentiment-analysis",
                              model="finiteautomata/bertweet-base-sentiment-analysis",
                              device="mps")
    print("✓ Sentiment model ready")

except Exception as e:
    print(f"\n✗ Error downloading models: {e}")
    print("\nTrying without GPU acceleration...")

    # Retry without GPU
    personality_model = pipeline("text-classification",
                                model="holistic-ai/personality_classifier")
    toxicity_model = pipeline("text-classification",
                             model="martin-ha/toxic-comment-model")
    sarcasm_model = pipeline("text-classification",
                            model="jkhan447/sarcasm-detection-RoBerta-base")
    sentiment_model = pipeline("sentiment-analysis",
                              model="finiteautomata/bertweet-base-sentiment-analysis")

print("\n" + "=" * 80)
print("Step 2: Testing models with sample texts...")
print("=" * 80)

for i, text in enumerate(test_texts, 1):
    print(f"\n\nTest {i}: \"{text}\"")
    print("-" * 80)

    try:
        with monitor.track_operation('holistic-ai/personality_classifier', 'inference', len(text)):
            personality_result = personality_model(text)[0]
        print(f"Personality:  {personality_result['label']} ({personality_result['score']:.2%} confidence)")
    except Exception as e:
        print(f"Personality:  Error - {e}")

    try:
        with monitor.track_operation('martin-ha/toxic-comment-model', 'inference', len(text)):
            toxicity_result = toxicity_model(text)[0]
        print(f"Toxicity:     {toxicity_result['label']} ({toxicity_result['score']:.2%} confidence)")
    except Exception as e:
        print(f"Toxicity:     Error - {e}")

    try:
        with monitor.track_operation('jkhan447/sarcasm-detection-RoBerta-base', 'inference', len(text)):
            sarcasm_result = sarcasm_model(text)[0]
        print(f"Sarcasm:      {sarcasm_result['label']} ({sarcasm_result['score']:.2%} confidence)")
    except Exception as e:
        print(f"Sarcasm:      Error - {e}")

    try:
        with monitor.track_operation('finiteautomata/bertweet-base-sentiment-analysis', 'inference', len(text)):
            sentiment_result = sentiment_model(text)[0]
        print(f"Sentiment:    {sentiment_result['label']} ({sentiment_result['score']:.2%} confidence)")
    except Exception as e:
        print(f"Sentiment:    Error - {e}")

print("\n\n" + "=" * 80)
print("✓ All models downloaded and tested successfully!")
print("=" * 80)

# Print performance summary
monitor.print_summary()

# Save metrics
print("Saving performance metrics...")
metrics_file = monitor.save_metrics()
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
print("1. Open the performance dashboard to view detailed metrics")
print("2. Create Hugging Face token at: https://huggingface.co/settings/tokens")
print("3. Run: huggingface-cli login")
print("4. Wait for theweekday model approval (you'll get an email)")
print("5. Download approved models with the code in MessageAnalyzerRecomendation.md")
print()

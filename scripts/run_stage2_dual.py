#!/usr/bin/env python3
"""
Run Stage 2 citation analysis with both Llama 3.2 and Qwen 2.5 in parallel.
"""

import sys
from pathlib import Path
import concurrent.futures
import json

sys.path.insert(0, str(Path(__file__).parent / "src"))

from stage2_citation_analyzer import CitationAnalyzer


def run_single_model(messages, phone_number, model_name, output_dir):
    """Run analysis with a single model."""
    print(f"\n[{model_name}] Starting analysis...")

    analyzer = CitationAnalyzer(model_name=model_name)
    results = analyzer.analyze_conversation(messages, phone_number)

    # Save results
    model_safe = model_name.replace(':', '_').replace('.', '_')
    output_json = output_dir / f"{phone_number}_citation_{model_safe}.json"

    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n[{model_name}] ✅ Complete! Saved to: {output_json.name}")

    return model_name, results


def main(phone_number: str = "309-948-9979"):
    """Run both models in parallel."""

    print(f"{'='*80}")
    print(f"STAGE 2 DUAL MODEL ANALYSIS: {phone_number}")
    print(f"{'='*80}\n")

    # Find conversation file
    conversations_dir = Path(__file__).parent / "data" / "output" / "all_conversations"
    matches = list(conversations_dir.glob(f"*{phone_number}*.json"))
    matches = [f for f in matches if not f.name.endswith("_analysis.json")]

    if not matches:
        print(f"❌ No conversation found for {phone_number}")
        return

    # Use the file with more messages
    conv_file = max(matches, key=lambda f: int(f.name.split('_')[1]))

    print(f"Loading: {conv_file.name}")

    # Load conversation
    with open(conv_file, 'r') as f:
        data = json.load(f)

    messages = data.get('messages', [])

    print(f"Total messages: {len(messages)}")
    print(f"\nRunning analysis with 2 models in parallel:")
    print(f"  - llama3.2")
    print(f"  - qwen2.5:7b")
    print()

    # Run both models in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_llama = executor.submit(
            run_single_model,
            messages,
            phone_number,
            "llama3.2",
            conversations_dir
        )

        future_qwen = executor.submit(
            run_single_model,
            messages,
            phone_number,
            "qwen2.5:7b",
            conversations_dir
        )

        # Wait for both to complete
        results = {}
        errors = {}
        for future in concurrent.futures.as_completed([future_llama, future_qwen]):
            try:
                model_name, result = future.result()
                results[model_name] = result
            except Exception as e:
                # Try to identify which model failed
                if future == future_llama:
                    model_name = "llama3.2"
                else:
                    model_name = "qwen2.5:7b"
                errors[model_name] = str(e)
                print(f"\n[{model_name}] ❌ Error: {e}")

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE!")
    print(f"{'='*80}\n")

    # Print results
    if results:
        print("Model Comparison:")
        for model_name, result in results.items():
            print(f"\n{model_name}:")
            print(f"  Response length: {result['response_length']} characters")
            if 'performance' in result:
                print(f"  Time: {result['performance']['elapsed_minutes']:.2f} minutes")
                print(f"  Memory: {result['performance']['memory_mb']:.2f} MB")

    # Print errors
    if errors:
        print("\n⚠️  ERRORS:")
        for model_name, error in errors.items():
            print(f"\n{model_name}: {error}")

    print(f"\n✅ Successful: {len(results)}/{len(results) + len(errors)}")
    print(f"\nFiles saved to: {conversations_dir}/")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run dual-model Stage 2 analysis")
    parser.add_argument("--phone", type=str, default="309-948-9979", help="Phone number to analyze")

    args = parser.parse_args()

    main(phone_number=args.phone)

#!/usr/bin/env python3
"""
Test the BERT personality and ToxicChat models to understand their inputs/outputs.
"""

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 80)
print("TESTING BERT PERSONALITY MODEL")
print("=" * 80)
print()

# Test 1: BERT Personality Model
print("Loading Minej/bert-base-personality...")
try:
    from transformers import BertTokenizer, BertForSequenceClassification
    import torch

    tokenizer = BertTokenizer.from_pretrained("Minej/bert-base-personality")
    model = BertForSequenceClassification.from_pretrained("Minej/bert-base-personality")

    print("✓ Model loaded successfully\n")

    # Test input
    test_text = "I love going to parties and meeting new people! Social events are so exciting."

    print(f"Test input: '{test_text}'\n")

    # Tokenize
    inputs = tokenizer(test_text, return_tensors="pt", truncation=True, max_length=512)
    print(f"Tokenized input shape: {inputs['input_ids'].shape}")

    # Get prediction
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = outputs.logits.detach().cpu().numpy()

    print(f"Output shape: {predictions.shape}")
    print(f"Raw output: {predictions[0]}")

    # Labels
    label_names = ['Extroversion', 'Neuroticism', 'Agreeableness', 'Conscientiousness', 'Openness']
    print(f"\nBig 5 Traits:")
    for i, label in enumerate(label_names):
        print(f"  {label}: {predictions[0][i]:.4f}")

    print("\n✓ BERT Personality model working correctly\n")

except Exception as e:
    print(f"✗ Error with BERT model: {e}\n")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TESTING TOXICCHAT MODEL")
print("=" * 80)
print()

# Test 2: ToxicChat Model
print("Loading lmsys/toxicchat-t5-large-v1.0...")
try:
    from transformers import T5Tokenizer, AutoModelForSeq2SeqLM

    # Use T5Tokenizer with legacy=False
    print("  Using T5Tokenizer with legacy=False...")
    tokenizer = T5Tokenizer.from_pretrained("lmsys/toxicchat-t5-large-v1.0", legacy=False)
    model = AutoModelForSeq2SeqLM.from_pretrained("lmsys/toxicchat-t5-large-v1.0")

    print("✓ Model loaded successfully\n")

    # Test input
    test_text = "You're an idiot and nobody likes you."
    prefix = "Predict toxicity: "

    print(f"Test input: '{test_text}'")
    print(f"Prefix: '{prefix}'\n")

    # Tokenize
    inputs = tokenizer.encode(prefix + test_text, return_tensors="pt", truncation=True, max_length=512)
    print(f"Tokenized input shape: {inputs.shape}")

    # Generate prediction
    outputs = model.generate(inputs, max_new_tokens=10)
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print(f"Raw output: {decoded}")

    # Parse output (should be "0" or "1")
    is_toxic = decoded.strip() == "1"
    print(f"\nParsed result: {'TOXIC' if is_toxic else 'NON-TOXIC'}")

    print("\n✓ ToxicChat model working correctly\n")

except Exception as e:
    print(f"✗ Error with ToxicChat model: {e}\n")
    import traceback
    traceback.print_exc()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nBoth models tested. Check output above for details.")

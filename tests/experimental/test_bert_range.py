#!/usr/bin/env python3
"""Test the actual output range of bert-base-personality."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from transformers import BertTokenizer, BertForSequenceClassification

tokenizer = BertTokenizer.from_pretrained("Minej/bert-base-personality")
model = BertForSequenceClassification.from_pretrained("Minej/bert-base-personality")

test_texts = [
    "I love parties! I'm always excited to meet new people and make friends!",  # High extraversion
    "I prefer to stay home alone and avoid social gatherings.",  # Low extraversion
    "I'm constantly worried and anxious about everything.",  # High neuroticism
    "I'm calm and never get stressed about anything.",  # Low neuroticism
    "",  # Empty
    "a",  # Minimal
]

label_names = ['Extroversion', 'Neuroticism', 'Agreeableness', 'Conscientiousness', 'Openness']

print("Testing bert-base-personality output ranges:")
print("=" * 80)

all_values = []

for text in test_texts:
    if not text:
        continue
    inputs = tokenizer(text, truncation=True, padding=True, return_tensors="pt")
    outputs = model(**inputs)
    predictions = outputs.logits.squeeze().detach().numpy()
    result = {label_names[i]: float(predictions[i]) for i in range(len(label_names))}

    print(f"\nText: {text[:60]}...")
    print(f"Scores: {result}")

    all_values.extend(result.values())

print("\n" + "=" * 80)
print(f"OBSERVED RANGE: {min(all_values):.3f} to {max(all_values):.3f}")
print(f"Mean: {sum(all_values)/len(all_values):.3f}")
print("\nConclusion: These are RAW LOGITS, not normalized 0-1 scores!")
print("We need to normalize them for comparison.")

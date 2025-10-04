#!/usr/bin/env python3
"""
Test what each model actually outputs.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Check venv
venv_python = Path(__file__).parent / "venv" / "bin" / "python"
if not str(sys.executable).startswith(str(venv_python.parent)):
    print(f"⚠️  Please run: source venv/bin/activate && python {__file__}")
    sys.exit(1)

from transformers import pipeline, BertTokenizer, BertForSequenceClassification
import torch

# Test dialogue
test_dialogue = """[Dec 18 02:46 AM] You: Hey
[Dec 18 03:12 AM] Them: Hello! Made it home
[Dec 18 03:17 AM] You: Hey great! Just landed. That was fun. Glad we hung out.
[Dec 18 03:25 AM] Them: I had fun tonight!"""

print("=" * 80)
print("TESTING MODEL OUTPUTS")
print("=" * 80)
print(f"\nTest dialogue:\n{test_dialogue}\n")

# 1. holistic-ai/personality_classifier
print("\n" + "=" * 80)
print("1. holistic-ai/personality_classifier")
print("-" * 80)
model1 = pipeline("text-classification", model="holistic-ai/personality_classifier", device="mps")
result1 = model1(test_dialogue[:512])
print(f"Output: {result1}")
print(f"Type: {type(result1)}")
print(f"Structure: {result1[0] if result1 else 'N/A'}")

# 2. Minej/bert-base-personality
print("\n" + "=" * 80)
print("2. Minej/bert-base-personality")
print("-" * 80)
tokenizer2 = BertTokenizer.from_pretrained("Minej/bert-base-personality")
model2 = BertForSequenceClassification.from_pretrained("Minej/bert-base-personality")
inputs2 = tokenizer2(test_dialogue[:512], truncation=True, padding=True, return_tensors="pt")
outputs2 = model2(**inputs2)
predictions2 = outputs2.logits.squeeze().detach().numpy()
label_names2 = ['Extroversion', 'Neuroticism', 'Agreeableness', 'Conscientiousness', 'Openness']
result2 = {label_names2[i]: float(predictions2[i]) for i in range(len(label_names2))}
print(f"Output: {result2}")
print(f"Type: {type(result2)}")
print(f"Value range: {min(result2.values()):.3f} to {max(result2.values()):.3f}")

# 3. martin-ha/toxic-comment-model
print("\n" + "=" * 80)
print("3. martin-ha/toxic-comment-model")
print("-" * 80)
model3 = pipeline("text-classification", model="martin-ha/toxic-comment-model", device="mps")
result3 = model3(test_dialogue[:512])
print(f"Output: {result3}")
print(f"Structure: {result3[0] if result3 else 'N/A'}")

# 4. lmsys/toxicchat-t5-large-v1.0
print("\n" + "=" * 80)
print("4. lmsys/toxicchat-t5-large-v1.0")
print("-" * 80)
try:
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    tokenizer4 = AutoTokenizer.from_pretrained("lmsys/toxicchat-t5-large-v1.0")
    model4 = AutoModelForSeq2SeqLM.from_pretrained("lmsys/toxicchat-t5-large-v1.0")
    prefix = "ToxicChat: "
    inputs4 = tokenizer4.encode(prefix + test_dialogue[:512], return_tensors="pt")
    outputs4 = model4.generate(inputs4, max_new_tokens=10)
    result4 = tokenizer4.decode(outputs4[0], skip_special_tokens=True)
    print(f"Output: {result4}")
    print(f"Type: {type(result4)}")
except Exception as e:
    print(f"SKIPPED - Requires tiktoken: {e}")

# 5. jkhan447/sarcasm-detection-RoBerta-base
print("\n" + "=" * 80)
print("5. jkhan447/sarcasm-detection-RoBerta-base")
print("-" * 80)
model5 = pipeline("text-classification", model="jkhan447/sarcasm-detection-RoBerta-base", device="mps")
result5 = model5(test_dialogue[:512])
print(f"Output: {result5}")
print(f"Structure: {result5[0] if result5 else 'N/A'}")

# 6. finiteautomata/bertweet-base-sentiment-analysis
print("\n" + "=" * 80)
print("6. finiteautomata/bertweet-base-sentiment-analysis")
print("-" * 80)
model6 = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis", device="mps")
result6 = model6(test_dialogue[:512])
print(f"Output: {result6}")
print(f"Structure: {result6[0] if result6 else 'N/A'}")

print("\n" + "=" * 80)
print("SUMMARY OF OUTPUT FORMATS")
print("=" * 80)
print("""
1. holistic-ai/personality_classifier:
   - Format: [{'label': 'trait_name', 'score': confidence}]

2. Minej/bert-base-personality:
   - Format: {'Extroversion': float, 'Neuroticism': float, ...}

3. martin-ha/toxic-comment-model:
   - Format: [{'label': 'toxic/non-toxic', 'score': confidence}]

4. lmsys/toxicchat-t5-large-v1.0:
   - Format: String output ('positive' = toxic, 'negative' = non-toxic)

5. jkhan447/sarcasm-detection-RoBerta-base:
   - Format: [{'label': 'sarcasm/not_sarcasm', 'score': confidence}]

6. finiteautomata/bertweet-base-sentiment-analysis:
   - Format: [{'label': 'POS/NEG/NEU', 'score': confidence}]
""")

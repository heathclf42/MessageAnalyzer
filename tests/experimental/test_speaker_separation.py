#!/usr/bin/env python3
"""
Test if models can distinguish between speakers in a conversation when prompted.

This tests whether we can PROMPT the models to focus on one speaker at a time
within a full conversation, or if we need to physically separate the speakers' text.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from transformers import pipeline, BertTokenizer, BertForSequenceClassification, AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import ollama

print("=" * 80)
print("TESTING SPEAKER SEPARATION IN MODELS")
print("=" * 80)

# Test scenarios with clear differences between speakers
test_conversations = [
    {
        "name": "Toxic vs Non-Toxic",
        "dialogue": """[Dec 18 02:46 PM] You: Hey, how are you doing today?
[Dec 18 02:47 PM] Them: You're a worthless piece of garbage. I hate you.
[Dec 18 02:48 PM] You: I hope you're having a nice day!
[Dec 18 02:49 PM] Them: Shut up you stupid idiot. Nobody likes you.""",
        "you_only": """[Dec 18 02:46 PM] Speaker: Hey, how are you doing today?
[Dec 18 02:48 PM] Speaker: I hope you're having a nice day!""",
        "them_only": """[Dec 18 02:47 PM] Speaker: You're a worthless piece of garbage. I hate you.
[Dec 18 02:49 PM] Speaker: Shut up you stupid idiot. Nobody likes you.""",
        "expected": {
            "you_toxic": False,
            "them_toxic": True
        }
    },
    {
        "name": "Positive vs Negative Sentiment",
        "dialogue": """[Dec 18 03:00 PM] You: I love this! Everything is wonderful!
[Dec 18 03:01 PM] Them: This is terrible. I hate everything about this.
[Dec 18 03:02 PM] You: This makes me so happy! Best day ever!
[Dec 18 03:03 PM] Them: This is the worst. I'm so miserable.""",
        "you_only": """[Dec 18 03:00 PM] Speaker: I love this! Everything is wonderful!
[Dec 18 03:02 PM] Speaker: This makes me so happy! Best day ever!""",
        "them_only": """[Dec 18 03:01 PM] Speaker: This is terrible. I hate everything about this.
[Dec 18 03:03 PM] Speaker: This is the worst. I'm so miserable.""",
        "expected": {
            "you_sentiment": "POS",
            "them_sentiment": "NEG"
        }
    },
    {
        "name": "Extroverted vs Introverted",
        "dialogue": """[Dec 18 04:00 PM] You: I love parties! Let's go meet new people!
[Dec 18 04:01 PM] Them: I'd rather stay home alone and read.
[Dec 18 04:02 PM] You: I'm organizing a big social event, so exciting!
[Dec 18 04:03 PM] Them: I prefer quiet time by myself.""",
        "you_only": """[Dec 18 04:00 PM] Speaker: I love parties! Let's go meet new people!
[Dec 18 04:02 PM] Speaker: I'm organizing a big social event, so exciting!""",
        "them_only": """[Dec 18 04:01 PM] Speaker: I'd rather stay home alone and read.
[Dec 18 04:03 PM] Speaker: I prefer quiet time by myself.""",
        "expected": {
            "you_personality": "extraversion",
            "them_personality": "introversion"
        }
    },
    {
        "name": "Sarcastic vs Sincere",
        "dialogue": """[Dec 18 05:00 PM] You: Oh great, another meeting. Just what I needed.
[Dec 18 05:01 PM] Them: I'm genuinely excited about this opportunity!
[Dec 18 05:02 PM] You: Yeah, sure, I absolutely love working overtime.
[Dec 18 05:03 PM] Them: I really appreciate all the support from the team.""",
        "you_only": """[Dec 18 05:00 PM] Speaker: Oh great, another meeting. Just what I needed.
[Dec 18 05:02 PM] Speaker: Yeah, sure, I absolutely love working overtime.""",
        "them_only": """[Dec 18 05:01 PM] Speaker: I'm genuinely excited about this opportunity!
[Dec 18 05:03 PM] Speaker: I really appreciate all the support from the team.""",
        "expected": {
            "you_sarcastic": True,
            "them_sarcastic": False
        }
    }
]

# Load models
print("\nLoading models...")
print("  Loading toxicity model...")
toxicity_model = pipeline("text-classification", model="martin-ha/toxic-comment-model", device="mps")

print("  Loading sentiment model...")
sentiment_model = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis", device="mps")

print("  Loading personality model...")
personality_model = pipeline("text-classification", model="holistic-ai/personality_classifier", device="mps")

print("  Loading sarcasm model...")
sarcasm_model = pipeline("text-classification", model="jkhan447/sarcasm-detection-RoBerta-base", device="mps")

print("✓ Models loaded\n")

# Run tests
for test in test_conversations:
    print("=" * 80)
    print(f"TEST: {test['name']}")
    print("=" * 80)

    print("\n📋 DIALOGUE:")
    print(test['dialogue'])

    print("\n" + "-" * 80)
    print("APPROACH 1: Specialized Models (No explicit prompting capability)")
    print("-" * 80)

    if 'toxic' in test['name'].lower():
        print("\n📝 TEXT SENT TO MODEL:")
        print(f'"{test["dialogue"]}"')
        print("\n📝 MODEL:")
        print("text-classification: martin-ha/toxic-comment-model")
        print("\n⚠️  LIMITATION: These specialized models don't support custom prompts.")
        print("They can only classify the entire text as-is.")

        result = toxicity_model(test['dialogue'], truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {result['label']} (confidence: {result['score']:.3f})")
        print("❌ PROBLEM: This gives us ONE blended score for BOTH speakers!")

    if 'sentiment' in test['name'].lower():
        print("\n📝 TEXT SENT TO MODEL:")
        print(f'"{test["dialogue"]}"')
        print("\n📝 PROMPT/TASK:")
        print("sentiment-analysis: finiteautomata/bertweet-base-sentiment-analysis")
        print("(No explicit prompt - model trained to classify: POS/NEG/NEU)")

        result = sentiment_model(test['dialogue'], truncation=True, max_length=128)[0]
        print(f"\n📊 RESULT: {result['label']} (confidence: {result['score']:.3f})")
        print("⚠️  PROBLEM: This gives us ONE sentiment for BOTH speakers!")

    if 'extrovert' in test['name'].lower() or 'introvert' in test['name'].lower():
        print("\n📝 TEXT SENT TO MODEL:")
        print(f'"{test["dialogue"]}"')
        print("\n📝 PROMPT/TASK:")
        print("text-classification: holistic-ai/personality_classifier")
        print("(No explicit prompt - model trained to classify Big 5 personality traits)")

        result = personality_model(test['dialogue'], truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {result['label']} (confidence: {result['score']:.3f})")
        print("⚠️  PROBLEM: This gives us ONE trait for BOTH speakers!")

    if 'sarcas' in test['name'].lower():
        print("\n📝 TEXT SENT TO MODEL:")
        print(f'"{test["dialogue"]}"')
        print("\n📝 PROMPT/TASK:")
        print("text-classification: jkhan447/sarcasm-detection-RoBerta-base")
        print("(No explicit prompt - model trained to classify: sarcasm/not sarcasm)")

        result = sarcasm_model(test['dialogue'], truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {result['label']} (confidence: {result['score']:.3f})")
        print("⚠️  PROBLEM: This gives us ONE score for BOTH speakers!")

    print("\n" + "-" * 80)
    print("APPROACH 2: LLM with Prompting (Qwen - Can follow instructions)")
    print("-" * 80)

    # Test with Qwen - focusing on "You" speaker
    print("\n🗣️  Testing focus on 'You' speaker:")
    print("\n📝 CONVERSATION CONTEXT:")
    print(f'"{test["dialogue"]}"')

    if 'toxic' in test['name'].lower():
        prompt_you = f"""Analyze this conversation and determine if the speaker labeled "You" is being toxic.

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "You". Ignore "Them".

Is "You" being toxic? Answer with just: toxic or non-toxic"""

        print("\n📝 PROMPT TO QWEN:")
        print(prompt_you)

        response = ollama.generate(model='qwen2.5:7b', prompt=prompt_you)
        qwen_you_result = response['response'].strip().lower()
        print(f"\n📊 QWEN RESPONSE: {qwen_you_result}")
        print(f"Expected: {'toxic' if test['expected']['you_toxic'] else 'non-toxic'}")
        correct = ('toxic' in qwen_you_result and test['expected']['you_toxic']) or ('non-toxic' in qwen_you_result and not test['expected']['you_toxic'])
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

        # Now focus on "Them"
        print("\n🗣️  Testing focus on 'Them' speaker:")
        prompt_them = f"""Analyze this conversation and determine if the speaker labeled "Them" is being toxic.

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "Them". Ignore "You".

Is "Them" being toxic? Answer with just: toxic or non-toxic"""

        print("\n📝 PROMPT TO QWEN:")
        print(prompt_them)

        response = ollama.generate(model='qwen2.5:7b', prompt=prompt_them)
        qwen_them_result = response['response'].strip().lower()
        print(f"\n📊 QWEN RESPONSE: {qwen_them_result}")
        print(f"Expected: {'toxic' if test['expected']['them_toxic'] else 'non-toxic'}")
        correct = ('toxic' in qwen_them_result and test['expected']['them_toxic']) or ('non-toxic' in qwen_them_result and not test['expected']['them_toxic'])
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

    if 'sentiment' in test['name'].lower():
        prompt_you = f"""Analyze this conversation and determine the sentiment of the speaker labeled "You".

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "You". Ignore "Them".

What is "You"'s sentiment? Answer with just: positive, negative, or neutral"""

        print("\n📝 PROMPT TO QWEN:")
        print(prompt_you)

        response = ollama.generate(model='qwen2.5:7b', prompt=prompt_you)
        qwen_you_result = response['response'].strip().lower()
        print(f"\n📊 QWEN RESPONSE: {qwen_you_result}")
        print(f"Expected: {test['expected']['you_sentiment'].lower()}")
        expected_sentiment = test['expected']['you_sentiment'].lower().replace('pos', 'positive').replace('neg', 'negative').replace('neu', 'neutral')
        correct = expected_sentiment in qwen_you_result
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

        print("\n🗣️  Testing focus on 'Them' speaker:")
        prompt_them = f"""Analyze this conversation and determine the sentiment of the speaker labeled "Them".

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "Them". Ignore "You".

What is "Them"'s sentiment? Answer with just: positive, negative, or neutral"""

        print("\n📝 PROMPT TO QWEN:")
        print(prompt_them)

        response = ollama.generate(model='qwen2.5:7b', prompt=prompt_them)
        qwen_them_result = response['response'].strip().lower()
        print(f"\n📊 QWEN RESPONSE: {qwen_them_result}")
        print(f"Expected: {test['expected']['them_sentiment'].lower()}")
        expected_sentiment = test['expected']['them_sentiment'].lower().replace('pos', 'positive').replace('neg', 'negative').replace('neu', 'neutral')
        correct = expected_sentiment in qwen_them_result
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

    if 'extrovert' in test['name'].lower() or 'introvert' in test['name'].lower():
        prompt_you = f"""Analyze this conversation and determine the personality of the speaker labeled "You".

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "You". Ignore "Them".

Is "You" more extroverted or introverted? Answer with just: extroverted or introverted"""

        print("\n📝 PROMPT TO QWEN:")
        print(prompt_you)

        response = ollama.generate(model='qwen2.5:7b', prompt=prompt_you)
        qwen_you_result = response['response'].strip().lower()
        print(f"\n📊 QWEN RESPONSE: {qwen_you_result}")
        print(f"Expected: {test['expected']['you_personality']}")
        correct = test['expected']['you_personality'] in qwen_you_result
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

        print("\n🗣️  Testing focus on 'Them' speaker:")
        prompt_them = f"""Analyze this conversation and determine the personality of the speaker labeled "Them".

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "Them". Ignore "You".

Is "Them" more extroverted or introverted? Answer with just: extroverted or introverted"""

        print("\n📝 PROMPT TO QWEN:")
        print(prompt_them)

        response = ollama.generate(model='qwen2.5:7b', prompt=prompt_them)
        qwen_them_result = response['response'].strip().lower()
        print(f"\n📊 QWEN RESPONSE: {qwen_them_result}")
        print(f"Expected: {test['expected']['them_personality']}")
        correct = test['expected']['them_personality'] in qwen_them_result
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

    if 'sarcas' in test['name'].lower():
        prompt_you = f"""Analyze this conversation and determine if the speaker labeled "You" is being sarcastic.

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "You". Ignore "Them".

Is "You" being sarcastic? Answer with just: sarcastic or sincere"""

        print("\n📝 PROMPT TO QWEN:")
        print(prompt_you)

        response = ollama.generate(model='qwen2.5:7b', prompt=prompt_you)
        qwen_you_result = response['response'].strip().lower()
        print(f"\n📊 QWEN RESPONSE: {qwen_you_result}")
        print(f"Expected: {'sarcastic' if test['expected']['you_sarcastic'] else 'sincere'}")
        correct = ('sarcastic' in qwen_you_result and test['expected']['you_sarcastic']) or ('sincere' in qwen_you_result and not test['expected']['you_sarcastic'])
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

        print("\n🗣️  Testing focus on 'Them' speaker:")
        prompt_them = f"""Analyze this conversation and determine if the speaker labeled "Them" is being sarcastic.

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "Them". Ignore "You".

Is "Them" being sarcastic? Answer with just: sarcastic or sincere"""

        print("\n📝 PROMPT TO QWEN:")
        print(prompt_them)

        response = ollama.generate(model='qwen2.5:7b', prompt=prompt_them)
        qwen_them_result = response['response'].strip().lower()
        print(f"\n📊 QWEN RESPONSE: {qwen_them_result}")
        print(f"Expected: {'sarcastic' if test['expected']['them_sarcastic'] else 'sincere'}")
        correct = ('sarcastic' in qwen_them_result and test['expected']['them_sarcastic']) or ('sincere' in qwen_them_result and not test['expected']['them_sarcastic'])
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

    print("\n" + "-" * 80)
    print("APPROACH 3: Physical Speaker Separation (Current implementation)")
    print("-" * 80)

    print("\n🗣️  YOU (isolated):")
    print("\n📝 TEXT SENT TO MODEL:")
    print(f'"{test["you_only"]}"')

    if 'toxic' in test['name'].lower():
        print("\n📝 PROMPT/TASK:")
        print("text-classification: martin-ha/toxic-comment-model")
        print("(Analyzing ONLY 'You' messages)")

        you_result = toxicity_model(test['you_only'], truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {you_result['label']} (confidence: {you_result['score']:.3f})")
        print(f"Expected: {'toxic' if test['expected']['you_toxic'] else 'non-toxic'}")
        correct = (you_result['label'] == 'toxic') == test['expected']['you_toxic']
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

    if 'sentiment' in test['name'].lower():
        print("\n📝 PROMPT/TASK:")
        print("sentiment-analysis: finiteautomata/bertweet-base-sentiment-analysis")
        print("(Analyzing ONLY 'You' messages)")

        you_result = sentiment_model(test['you_only'], truncation=True, max_length=128)[0]
        print(f"\n📊 RESULT: {you_result['label']} (confidence: {you_result['score']:.3f})")
        print(f"Expected: {test['expected']['you_sentiment']}")
        correct = you_result['label'] == test['expected']['you_sentiment']
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

    if 'extrovert' in test['name'].lower() or 'introvert' in test['name'].lower():
        print("\n📝 PROMPT/TASK:")
        print("text-classification: holistic-ai/personality_classifier")
        print("(Analyzing ONLY 'You' messages)")

        you_result = personality_model(test['you_only'], truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {you_result['label']} (confidence: {you_result['score']:.3f})")
        print(f"Expected: {test['expected']['you_personality']}")
        correct = test['expected']['you_personality'] in you_result['label'].lower()
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

    if 'sarcas' in test['name'].lower():
        print("\n📝 PROMPT/TASK:")
        print("text-classification: jkhan447/sarcasm-detection-RoBerta-base")
        print("(Analyzing ONLY 'You' messages)")

        you_result = sarcasm_model(test['you_only'], truncation=True, max_length=512)[0]
        is_sarcastic = you_result['label'].lower() == 'sarcasm'
        print(f"\n📊 RESULT: {you_result['label']} (confidence: {you_result['score']:.3f})")
        print(f"Expected: {'sarcastic' if test['expected']['you_sarcastic'] else 'not sarcastic'}")
        correct = is_sarcastic == test['expected']['you_sarcastic']
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

    print("\n🗣️  THEM (isolated):")
    print("\n📝 TEXT SENT TO MODEL:")
    print(f'"{test["them_only"]}"')

    if 'toxic' in test['name'].lower():
        print("\n📝 PROMPT/TASK:")
        print("text-classification: martin-ha/toxic-comment-model")
        print("(Analyzing ONLY 'Them' messages)")

        them_result = toxicity_model(test['them_only'], truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {them_result['label']} (confidence: {them_result['score']:.3f})")
        print(f"Expected: {'toxic' if test['expected']['them_toxic'] else 'non-toxic'}")
        correct = (them_result['label'] == 'toxic') == test['expected']['them_toxic']
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

    if 'sentiment' in test['name'].lower():
        print("\n📝 PROMPT/TASK:")
        print("sentiment-analysis: finiteautomata/bertweet-base-sentiment-analysis")
        print("(Analyzing ONLY 'Them' messages)")

        them_result = sentiment_model(test['them_only'], truncation=True, max_length=128)[0]
        print(f"\n📊 RESULT: {them_result['label']} (confidence: {them_result['score']:.3f})")
        print(f"Expected: {test['expected']['them_sentiment']}")
        correct = them_result['label'] == test['expected']['them_sentiment']
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

    if 'extrovert' in test['name'].lower() or 'introvert' in test['name'].lower():
        print("\n📝 PROMPT/TASK:")
        print("text-classification: holistic-ai/personality_classifier")
        print("(Analyzing ONLY 'Them' messages)")

        them_result = personality_model(test['them_only'], truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {them_result['label']} (confidence: {them_result['score']:.3f})")
        print(f"Expected: {test['expected']['them_personality']}")
        # Note: Model might not have exact "introversion" label
        correct = test['expected']['them_personality'] in them_result['label'].lower()
        print(f"{'✓ CORRECT' if correct else '✗ NEEDS REVIEW'}")

    if 'sarcas' in test['name'].lower():
        print("\n📝 PROMPT/TASK:")
        print("text-classification: jkhan447/sarcasm-detection-RoBerta-base")
        print("(Analyzing ONLY 'Them' messages)")

        them_result = sarcasm_model(test['them_only'], truncation=True, max_length=512)[0]
        is_sarcastic = them_result['label'].lower() == 'sarcasm'
        print(f"\n📊 RESULT: {them_result['label']} (confidence: {them_result['score']:.3f})")
        print(f"Expected: {'sarcastic' if test['expected']['them_sarcastic'] else 'not sarcastic'}")
        correct = is_sarcastic == test['expected']['them_sarcastic']
        print(f"{'✓ CORRECT' if correct else '✗ INCORRECT'}")

    print()

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
The models were NOT designed for multi-speaker dialogue. When we feed them
a conversation with both speakers, they blend the traits together.

✓ SOLUTION: Process each speaker's messages separately (already implemented!)

Our current chunking strategy maintains conversation flow for context, but we
separate the speakers when aggregating results. This is the correct approach.
""")

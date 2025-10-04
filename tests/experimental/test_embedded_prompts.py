#!/usr/bin/env python3
"""
Test if models can follow embedded instructions to focus on one speaker.

Tests whether we can prepend instructions to conversation text and have
specialized models analyze only one speaker while considering full context.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from transformers import pipeline

print("=" * 80)
print("TESTING EMBEDDED PROMPT APPROACH")
print("=" * 80)
print("\nTesting if specialized models can follow embedded instructions")
print("to analyze one speaker at a time while considering full conversation.\n")

# Realistic test conversations with nuanced differences
test_conversations = [
    {
        "name": "Passive Aggression (Toxicity)",
        "dialogue": """[Mar 15 02:30 PM] You: Hey, did you get a chance to look at that email I sent?
[Mar 15 02:35 PM] Them: Yeah, I saw it. Why do you always wait until the last minute?
[Mar 15 02:36 PM] You: I mean, I sent it yesterday. That's not really last minute.
[Mar 15 02:38 PM] Them: Well it would be nice if you planned ahead for once. Some of us have other things to do.
[Mar 15 02:40 PM] You: Okay, I'll try to give more notice next time.
[Mar 15 02:42 PM] Them: Sure, like always.""",
        "metric": "toxicity",
        "expected": {
            "you_level": "low",
            "them_level": "high",
            "who_more": "Them"
        }
    },
    {
        "name": "Disappointment vs Optimism (Sentiment)",
        "dialogue": """[Mar 15 03:00 PM] You: The project presentation didn't go as well as I hoped.
[Mar 15 03:02 PM] Them: Yeah, but at least we got some good feedback on the design.
[Mar 15 03:04 PM] You: I guess. I just feel like we could have prepared more.
[Mar 15 03:06 PM] Them: Maybe, but I think we can use their suggestions to make it even better!
[Mar 15 03:08 PM] You: I don't know, seems like a lot of work to redo everything.
[Mar 15 03:10 PM] Them: It's not redoing - it's improving. This could actually make it stronger.""",
        "metric": "sentiment",
        "expected": {
            "you_level": "negative",
            "them_level": "positive",
            "who_more": "Them (more positive)"
        }
    },
    {
        "name": "Reserved vs Enthusiastic (Personality)",
        "dialogue": """[Mar 15 04:00 PM] You: There's a team happy hour Friday if you want to go.
[Mar 15 04:02 PM] Them: Oh absolutely! I love these things. We should invite the whole floor!
[Mar 15 04:04 PM] You: I mean, I'll probably just stop by for a bit.
[Mar 15 04:06 PM] Them: You should stay! Last time was so fun, we played games and everything!
[Mar 15 04:08 PM] You: Yeah, I might. I'll see how I'm feeling.
[Mar 15 04:10 PM] Them: Come on, it'll be great! I'm gonna organize some team bonding activities!""",
        "metric": "personality",
        "expected": {
            "you_level": "introverted",
            "them_level": "extroverted",
            "who_more": "Them (more extroverted)"
        }
    },
    {
        "name": "Mild Sarcasm vs Earnest (Sarcasm)",
        "dialogue": """[Mar 15 05:00 PM] You: Another mandatory training session scheduled for Friday afternoon.
[Mar 15 05:02 PM] Them: Oh no, really? That's the third one this month.
[Mar 15 05:04 PM] You: Yeah, can't wait. Nothing says 'productive' like sitting through slides at 4pm on a Friday.
[Mar 15 05:06 PM] Them: That's pretty inconvenient. Maybe we can ask if there's a recording?
[Mar 15 05:08 PM] You: Sure, because watching it later will be so much more exciting.
[Mar 15 05:10 PM] Them: Well, at least we could watch it when we're more focused.""",
        "metric": "sarcasm",
        "expected": {
            "you_level": "sarcastic",
            "them_level": "sincere",
            "who_more": "You (more sarcastic)"
        }
    }
]

# Load models
print("Loading models...")
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

    print("\n📋 ORIGINAL CONVERSATION:")
    print(test['dialogue'])
    print(f"\n✓ Expected: {test['expected']['who_more']}")

    # Test focusing on "You"
    print("\n" + "-" * 80)
    print("PASS 1: Analyzing 'You' speaker")
    print("-" * 80)

    if test['metric'] == 'toxicity':
        prompt_text = f"""The following is a conversation between two people. Analyze the toxicity of the speaker "You" based on the entire conversation context. Focus your analysis only on "You"'s behavior and language.

{test['dialogue']}"""

        print("\n📝 TEXT SENT TO MODEL:")
        print('"""')
        print(prompt_text)
        print('"""')

        result_you = toxicity_model(prompt_text, truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {result_you['label']} (confidence: {result_you['score']:.3f})")
        print(f"Expected level: {test['expected']['you_level']}")

    elif test['metric'] == 'sentiment':
        prompt_text = f"""The following is a conversation between two people. Analyze the overall sentiment of the speaker "You" based on the entire conversation context. Focus your analysis only on "You"'s messages.

{test['dialogue']}"""

        print("\n📝 TEXT SENT TO MODEL:")
        print('"""')
        print(prompt_text)
        print('"""')

        result_you = sentiment_model(prompt_text, truncation=True, max_length=128)[0]
        print(f"\n📊 RESULT: {result_you['label']} (confidence: {result_you['score']:.3f})")
        print(f"Expected: {test['expected']['you_level']}")

    elif test['metric'] == 'personality':
        prompt_text = f"""The following is a conversation between two people. Analyze the personality of the speaker "You" based on the entire conversation context. Focus your analysis only on "You"'s behavior and communication style.

{test['dialogue']}"""

        print("\n📝 TEXT SENT TO MODEL:")
        print('"""')
        print(prompt_text)
        print('"""')

        result_you = personality_model(prompt_text, truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {result_you['label']} (confidence: {result_you['score']:.3f})")
        print(f"Expected: {test['expected']['you_level']}")

    elif test['metric'] == 'sarcasm':
        prompt_text = f"""The following is a conversation between two people. Analyze whether the speaker "You" is being sarcastic based on the entire conversation context. Focus your analysis only on "You"'s messages.

{test['dialogue']}"""

        print("\n📝 TEXT SENT TO MODEL:")
        print('"""')
        print(prompt_text)
        print('"""')

        result_you = sarcasm_model(prompt_text, truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {result_you['label']} (confidence: {result_you['score']:.3f})")
        print(f"Expected: {test['expected']['you_level']}")

    # Test focusing on "Them"
    print("\n" + "-" * 80)
    print("PASS 2: Analyzing 'Them' speaker")
    print("-" * 80)

    if test['metric'] == 'toxicity':
        prompt_text = f"""The following is a conversation between two people. Analyze the toxicity of the speaker "Them" based on the entire conversation context. Focus your analysis only on "Them"'s behavior and language.

{test['dialogue']}"""

        print("\n📝 TEXT SENT TO MODEL:")
        print('"""')
        print(prompt_text)
        print('"""')

        result_them = toxicity_model(prompt_text, truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {result_them['label']} (confidence: {result_them['score']:.3f})")
        print(f"Expected level: {test['expected']['them_level']}")

    elif test['metric'] == 'sentiment':
        prompt_text = f"""The following is a conversation between two people. Analyze the overall sentiment of the speaker "Them" based on the entire conversation context. Focus your analysis only on "Them"'s messages.

{test['dialogue']}"""

        print("\n📝 TEXT SENT TO MODEL:")
        print('"""')
        print(prompt_text)
        print('"""')

        result_them = sentiment_model(prompt_text, truncation=True, max_length=128)[0]
        print(f"\n📊 RESULT: {result_them['label']} (confidence: {result_them['score']:.3f})")
        print(f"Expected: {test['expected']['them_level']}")

    elif test['metric'] == 'personality':
        prompt_text = f"""The following is a conversation between two people. Analyze the personality of the speaker "Them" based on the entire conversation context. Focus your analysis only on "Them"'s behavior and communication style.

{test['dialogue']}"""

        print("\n📝 TEXT SENT TO MODEL:")
        print('"""')
        print(prompt_text)
        print('"""')

        result_them = personality_model(prompt_text, truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {result_them['label']} (confidence: {result_them['score']:.3f})")
        print(f"Expected: {test['expected']['them_level']}")

    elif test['metric'] == 'sarcasm':
        prompt_text = f"""The following is a conversation between two people. Analyze whether the speaker "Them" is being sarcastic based on the entire conversation context. Focus your analysis only on "Them"'s messages.

{test['dialogue']}"""

        print("\n📝 TEXT SENT TO MODEL:")
        print('"""')
        print(prompt_text)
        print('"""')

        result_them = sarcasm_model(prompt_text, truncation=True, max_length=512)[0]
        print(f"\n📊 RESULT: {result_them['label']} (confidence: {result_them['score']:.3f})")
        print(f"Expected: {test['expected']['them_level']}")

    print("\n" + "-" * 80)
    print("ABSOLUTE SCORES")
    print("-" * 80)

    print(f"\n'You':   {result_you['label']} (confidence: {result_you['score']:.3f})")
    print(f"'Them':  {result_them['label']} (confidence: {result_them['score']:.3f})")

    print(f"\nExpected behavior: {test['expected']['who_more']}")
    print()

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("""
This test checks if specialized models can:
1. Follow embedded instructions in the text
2. Analyze one speaker while considering full conversation context
3. Produce different scores for different speakers appropriately

If the models consistently identify the expected speaker as scoring higher/lower,
then this approach works and we can use it in our implementation.

If not, we need to stick with physical speaker separation (current approach).
""")

#!/usr/bin/env python3
"""
Preview all prompts and text that will be sent to models.
Review this before running the actual test.
"""

# Test scenarios
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
        "metric": "toxicity"
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
        "metric": "sentiment"
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
        "metric": "personality"
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
        "metric": "sarcasm"
    }
]

print("=" * 80)
print("PREVIEW: WHAT WILL BE SENT TO EACH MODEL")
print("=" * 80)
print("\nThis shows all the text and prompts that will be sent during testing.")
print("Review these carefully before running the actual test.\n")

for test in test_conversations:
    print("\n" + "=" * 80)
    print(f"TEST SCENARIO: {test['name']}")
    print("=" * 80)

    print("\n" + "-" * 80)
    print("APPROACH 1: Specialized Models (No Prompting)")
    print("-" * 80)
    print("\n⚠️  These models don't support custom prompts - they only classify text as-is")
    print("\n📝 TEXT THAT WILL BE SENT:")
    print(f'"""\n{test["dialogue"]}\n"""')
    print("\n📊 MODEL: martin-ha/toxic-comment-model (or similar)")
    print("❌ LIMITATION: Returns ONE score for the entire text (both speakers blended)")

    print("\n" + "-" * 80)
    print("APPROACH 2: Qwen with Prompting (Testing speaker focus)")
    print("-" * 80)

    print("\n🗣️  PASS 1 - Focus on 'You' speaker:")
    print("-" * 40)

    if test['metric'] == 'toxicity':
        prompt = f"""Analyze this conversation and determine if the speaker labeled "You" is being toxic.

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "You". Ignore "Them".

Is "You" being toxic? Answer with just: toxic or non-toxic"""

        print("📝 PROMPT TO QWEN:")
        print('"""')
        print(prompt)
        print('"""')
        print("\n✓ Expected answer: non-toxic")

    elif test['metric'] == 'sentiment':
        prompt = f"""Analyze this conversation and determine the sentiment of the speaker labeled "You".

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "You". Ignore "Them".

What is "You"'s sentiment? Answer with just: positive, negative, or neutral"""

        print("📝 PROMPT TO QWEN:")
        print('"""')
        print(prompt)
        print('"""')
        print("\n✓ Expected answer: positive")

    elif test['metric'] == 'personality':
        prompt = f"""Analyze this conversation and determine the personality of the speaker labeled "You".

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "You". Ignore "Them".

Is "You" more extroverted or introverted? Answer with just: extroverted or introverted"""

        print("📝 PROMPT TO QWEN:")
        print('"""')
        print(prompt)
        print('"""')
        print("\n✓ Expected answer: extroverted")

    elif test['metric'] == 'sarcasm':
        prompt = f"""Analyze this conversation and determine if the speaker labeled "You" is being sarcastic.

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "You". Ignore "Them".

Is "You" being sarcastic? Answer with just: sarcastic or sincere"""

        print("📝 PROMPT TO QWEN:")
        print('"""')
        print(prompt)
        print('"""')
        print("\n✓ Expected answer: sarcastic")

    print("\n🗣️  PASS 2 - Focus on 'Them' speaker:")
    print("-" * 40)

    if test['metric'] == 'toxicity':
        prompt = f"""Analyze this conversation and determine if the speaker labeled "Them" is being toxic.

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "Them". Ignore "You".

Is "Them" being toxic? Answer with just: toxic or non-toxic"""

        print("📝 PROMPT TO QWEN:")
        print('"""')
        print(prompt)
        print('"""')
        print("\n✓ Expected answer: toxic")

    elif test['metric'] == 'sentiment':
        prompt = f"""Analyze this conversation and determine the sentiment of the speaker labeled "Them".

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "Them". Ignore "You".

What is "Them"'s sentiment? Answer with just: positive, negative, or neutral"""

        print("📝 PROMPT TO QWEN:")
        print('"""')
        print(prompt)
        print('"""')
        print("\n✓ Expected answer: negative")

    elif test['metric'] == 'personality':
        prompt = f"""Analyze this conversation and determine the personality of the speaker labeled "Them".

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "Them". Ignore "You".

Is "Them" more extroverted or introverted? Answer with just: extroverted or introverted"""

        print("📝 PROMPT TO QWEN:")
        print('"""')
        print(prompt)
        print('"""')
        print("\n✓ Expected answer: introverted")

    elif test['metric'] == 'sarcasm':
        prompt = f"""Analyze this conversation and determine if the speaker labeled "Them" is being sarcastic.

Conversation:
{test['dialogue']}

Focus ONLY on the messages from "Them". Ignore "You".

Is "Them" being sarcastic? Answer with just: sarcastic or sincere"""

        print("📝 PROMPT TO QWEN:")
        print('"""')
        print(prompt)
        print('"""')
        print("\n✓ Expected answer: sincere")

    print("\n" + "-" * 80)
    print("APPROACH 3: Physical Separation (Current Implementation)")
    print("-" * 80)

    print("\n🗣️  YOU messages (isolated):")
    print('"""')
    print(test['you_only'])
    print('"""')
    print("\n📊 Sent to specialized models separately")

    print("\n🗣️  THEM messages (isolated):")
    print('"""')
    print(test['them_only'])
    print('"""')
    print("\n📊 Sent to specialized models separately")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("""
This preview shows 3 approaches:

1. APPROACH 1: Specialized models with full dialogue
   - No prompting capability
   - Returns blended score for both speakers

2. APPROACH 2: Qwen with explicit prompts
   - Full conversation + prompt to focus on specific speaker
   - Tests if prompting can isolate speaker traits
   - Runs twice: once for "You", once for "Them"

3. APPROACH 3: Physical speaker separation
   - Separate text by speaker before sending
   - Current implementation in llm_analyzer.py

Review the prompts above. If they look good, run:
  python test_speaker_separation.py

If you want to edit the prompts, modify the test_speaker_separation.py file.
""")

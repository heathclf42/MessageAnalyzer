#!/usr/bin/env python3
"""
Psychological and linguistic analysis of conversations.
Analyzes Jungian archetypes, Enneagram types, MBTI, attachment styles, and more.
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
import statistics

# Jungian Archetype Keywords
ARCHETYPE_KEYWORDS = {
    "Hero": ["brave", "challenge", "overcome", "fight", "strong", "courage", "victory", "achieve", "succeed", "win", "conquer"],
    "Sage": ["understand", "learn", "know", "wisdom", "truth", "think", "analyze", "research", "study", "insight", "realize"],
    "Explorer": ["adventure", "discover", "new", "explore", "travel", "freedom", "experience", "different", "journey", "wanderlust"],
    "Innocent": ["hope", "happy", "simple", "trust", "faith", "optimistic", "pure", "good", "believe", "dream", "wish"],
    "Caregiver": ["help", "care", "support", "protect", "nurture", "love", "give", "comfort", "serve", "sacrifice"],
    "Rebel": ["break", "change", "revolution", "different", "unique", "against", "challenge", "disrupt", "rebel", "unconventional"],
    "Magician": ["transform", "create", "vision", "manifest", "power", "magic", "change", "innovate", "make happen"],
    "Lover": ["love", "passion", "beauty", "desire", "romance", "intimate", "connection", "feel", "heart", "emotional"],
    "Jester": ["fun", "laugh", "joke", "play", "humor", "enjoy", "happy", "silly", "funny", "lighthearted"],
    "Everyperson": ["normal", "ordinary", "regular", "like everyone", "common", "belong", "fit in", "average", "relatable"],
    "Ruler": ["control", "lead", "power", "authority", "command", "organize", "manage", "direct", "responsible", "order"],
    "Creator": ["create", "build", "make", "design", "imagine", "art", "invent", "express", "original", "vision"]
}

# Enneagram Type Keywords
ENNEAGRAM_KEYWORDS = {
    "Type 1 (Perfectionist)": ["should", "must", "right", "wrong", "perfect", "improve", "correct", "better", "proper", "ideal"],
    "Type 2 (Helper)": ["help", "need", "care", "support", "for you", "give", "love", "there for", "assist"],
    "Type 3 (Achiever)": ["success", "goal", "achieve", "accomplish", "win", "best", "excellent", "performance", "impress"],
    "Type 4 (Individualist)": ["unique", "different", "special", "feel", "emotional", "authentic", "deep", "meaningful"],
    "Type 5 (Investigator)": ["think", "analyze", "understand", "know", "research", "learn", "study", "observe", "figure out"],
    "Type 6 (Loyalist)": ["worry", "anxious", "safe", "trust", "loyal", "cautious", "prepared", "what if", "concerned"],
    "Type 7 (Enthusiast)": ["fun", "exciting", "adventure", "possibilities", "enjoy", "experience", "new", "happy", "amazing"],
    "Type 8 (Challenger)": ["strong", "power", "control", "fight", "protect", "direct", "challenge", "intense", "assert"],
    "Type 9 (Peacemaker)": ["peace", "calm", "agree", "harmony", "comfortable", "go with", "whatever", "easy", "avoid conflict"]
}

# MBTI Indicators
MBTI_INDICATORS = {
    "Introversion": ["quiet", "alone", "recharge", "think before", "inner", "private", "few close", "listen"],
    "Extraversion": ["energized by people", "talk", "social", "outgoing", "group", "express", "share", "external"],
    "Sensing": ["practical", "concrete", "details", "facts", "present", "realistic", "specific", "experience"],
    "Intuition": ["future", "possibility", "pattern", "meaning", "abstract", "imagine", "theory", "big picture"],
    "Thinking": ["logical", "analyze", "objective", "fair", "reason", "decide", "truth", "principle"],
    "Feeling": ["feel", "empathy", "harmony", "values", "care about", "personal", "relationship", "impact on people"],
    "Judging": ["plan", "organize", "decide", "structure", "schedule", "order", "control", "deadline"],
    "Perceiving": ["flexible", "adapt", "spontaneous", "open", "explore", "go with flow", "last minute", "options"]
}

# Attachment Style Keywords
ATTACHMENT_KEYWORDS = {
    "Secure": ["comfortable", "trust", "close", "independent", "honest", "communicate", "balance", "healthy"],
    "Anxious": ["worry", "need reassurance", "fear losing", "clingy", "overthink", "insecure", "anxious", "please"],
    "Avoidant": ["space", "independent", "distance", "uncomfortable with", "pull away", "avoid", "emotionally distant"],
    "Disorganized": ["confusing", "mixed signals", "push and pull", "fear and want", "chaotic", "unpredictable"]
}

# Emotional Language Patterns
EMOTION_KEYWORDS = {
    "Joy": ["happy", "excited", "love", "joy", "wonderful", "amazing", "great", "fantastic", "perfect"],
    "Sadness": ["sad", "depressed", "down", "hurt", "pain", "cry", "miss", "lonely", "disappointed"],
    "Anger": ["angry", "mad", "furious", "annoyed", "frustrated", "pissed", "irritated", "rage"],
    "Fear": ["afraid", "scared", "worry", "anxious", "nervous", "panic", "terrified", "fear"],
    "Love": ["love", "adore", "cherish", "care", "affection", "heart", "romance", "passion"],
    "Gratitude": ["thank", "grateful", "appreciate", "thanks", "thankful", "blessing"]
}

def count_keywords(text, keyword_dict):
    """Count keyword matches in text"""
    text_lower = text.lower()
    scores = {}
    for category, keywords in keyword_dict.items():
        count = sum(1 for keyword in keywords if keyword in text_lower)
        scores[category] = count
    return scores

def analyze_archetypes(messages):
    """Analyze Jungian archetypes based on language patterns"""
    all_text = " ".join([msg['text'] for msg in messages])
    scores = count_keywords(all_text, ARCHETYPE_KEYWORDS)

    # Normalize scores
    total = sum(scores.values()) or 1
    percentages = {k: (v / total) * 100 for k, v in scores.items()}

    # Get top 3 archetypes
    top_archetypes = sorted(percentages.items(), key=lambda x: x[1], reverse=True)[:3]

    return {
        "scores": percentages,
        "primary": top_archetypes[0][0] if top_archetypes else "Unknown",
        "top_three": [{"archetype": arch, "percentage": pct} for arch, pct in top_archetypes]
    }

def analyze_enneagram(messages):
    """Analyze likely Enneagram type"""
    all_text = " ".join([msg['text'] for msg in messages])
    scores = count_keywords(all_text, ENNEAGRAM_KEYWORDS)

    total = sum(scores.values()) or 1
    percentages = {k: (v / total) * 100 for k, v in scores.items()}

    primary_type = max(percentages.items(), key=lambda x: x[1]) if percentages else ("Unknown", 0)

    return {
        "scores": percentages,
        "likely_type": primary_type[0],
        "confidence": primary_type[1]
    }

def analyze_mbti(messages):
    """Analyze MBTI indicators"""
    all_text = " ".join([msg['text'] for msg in messages])
    scores = count_keywords(all_text, MBTI_INDICATORS)

    # Determine preferences
    i_vs_e = "I" if scores.get("Introversion", 0) > scores.get("Extraversion", 0) else "E"
    n_vs_s = "N" if scores.get("Intuition", 0) > scores.get("Sensing", 0) else "S"
    t_vs_f = "T" if scores.get("Thinking", 0) > scores.get("Feeling", 0) else "F"
    j_vs_p = "J" if scores.get("Judging", 0) > scores.get("Perceiving", 0) else "P"

    mbti_type = f"{i_vs_e}{n_vs_s}{t_vs_f}{j_vs_p}"

    return {
        "type": mbti_type,
        "scores": scores,
        "preferences": {
            "I_vs_E": {"preference": i_vs_e, "I": scores.get("Introversion", 0), "E": scores.get("Extraversion", 0)},
            "N_vs_S": {"preference": n_vs_s, "N": scores.get("Intuition", 0), "S": scores.get("Sensing", 0)},
            "T_vs_F": {"preference": t_vs_f, "T": scores.get("Thinking", 0), "F": scores.get("Feeling", 0)},
            "J_vs_P": {"preference": j_vs_p, "J": scores.get("Judging", 0), "P": scores.get("Perceiving", 0)}
        }
    }

def analyze_attachment_style(messages):
    """Analyze attachment style"""
    all_text = " ".join([msg['text'] for msg in messages])
    scores = count_keywords(all_text, ATTACHMENT_KEYWORDS)

    total = sum(scores.values()) or 1
    percentages = {k: (v / total) * 100 for k, v in scores.items()}

    primary_style = max(percentages.items(), key=lambda x: x[1]) if percentages else ("Unknown", 0)

    return {
        "scores": percentages,
        "likely_style": primary_style[0],
        "confidence": primary_style[1]
    }

def analyze_emotions(messages):
    """Analyze emotional patterns"""
    all_text = " ".join([msg['text'] for msg in messages])
    scores = count_keywords(all_text, EMOTION_KEYWORDS)

    total = sum(scores.values()) or 1
    percentages = {k: (v / total) * 100 for k, v in scores.items()}

    return {
        "scores": percentages,
        "dominant_emotion": max(percentages.items(), key=lambda x: x[1])[0] if percentages else "Unknown"
    }

def analyze_communication_patterns(messages, is_from_me):
    """Analyze communication patterns for a specific person"""
    person_messages = [msg for msg in messages if msg['is_from_me'] == is_from_me]

    if not person_messages:
        return None

    # Message lengths
    lengths = [len(msg['text']) for msg in person_messages]

    # Questions vs statements
    questions = sum(1 for msg in person_messages if '?' in msg['text'])

    # Emoji usage
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map
                               u"\U0001F1E0-\U0001F1FF"  # flags
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    emoji_count = sum(1 for msg in person_messages if emoji_pattern.search(msg['text']))

    # Exclamation usage
    exclamations = sum(msg['text'].count('!') for msg in person_messages)

    return {
        "message_count": len(person_messages),
        "avg_message_length": statistics.mean(lengths) if lengths else 0,
        "median_message_length": statistics.median(lengths) if lengths else 0,
        "question_percentage": (questions / len(person_messages)) * 100 if person_messages else 0,
        "emoji_usage": (emoji_count / len(person_messages)) * 100 if person_messages else 0,
        "exclamation_usage": exclamations / len(person_messages) if person_messages else 0
    }

def analyze_relationship_dynamics(messages):
    """Analyze relationship dynamics"""
    you_messages = [msg for msg in messages if msg['is_from_me']]
    them_messages = [msg for msg in messages if not msg['is_from_me']]

    # Who initiates more
    # Simple heuristic: look for time gaps > 2 hours
    initiations = {"you": 0, "them": 0}

    for i in range(1, len(messages)):
        prev_msg = messages[i-1]
        curr_msg = messages[i]

        if prev_msg['date'] and curr_msg['date']:
            prev_time = datetime.fromisoformat(prev_msg['date'])
            curr_time = datetime.fromisoformat(curr_msg['date'])
            time_diff = (curr_time - prev_time).total_seconds() / 3600  # hours

            if time_diff > 2:  # New conversation thread
                if curr_msg['is_from_me']:
                    initiations["you"] += 1
                else:
                    initiations["them"] += 1

    # Response times (simplified - just count immediate responses)
    your_quick_responses = 0
    their_quick_responses = 0

    for i in range(1, len(messages)):
        prev_msg = messages[i-1]
        curr_msg = messages[i]

        if prev_msg['date'] and curr_msg['date']:
            prev_time = datetime.fromisoformat(prev_msg['date'])
            curr_time = datetime.fromisoformat(curr_msg['date'])
            time_diff = (curr_time - prev_time).total_seconds() / 60  # minutes

            if time_diff < 5:  # Quick response
                if curr_msg['is_from_me'] and not prev_msg['is_from_me']:
                    your_quick_responses += 1
                elif not curr_msg['is_from_me'] and prev_msg['is_from_me']:
                    their_quick_responses += 1

    return {
        "initiation": {
            "you": initiations["you"],
            "them": initiations["them"],
            "who_initiates_more": "You" if initiations["you"] > initiations["them"] else "Them"
        },
        "responsiveness": {
            "your_quick_responses": your_quick_responses,
            "their_quick_responses": their_quick_responses
        },
        "message_balance": {
            "you": len(you_messages),
            "them": len(them_messages),
            "ratio": len(you_messages) / len(them_messages) if them_messages else 0
        }
    }

def analyze_conversation(conversation_json_path):
    """Main analysis function"""

    with open(conversation_json_path, 'r', encoding='utf-8') as f:
        conv_data = json.load(f)

    messages = conv_data['messages']

    # Separate YOUR messages from THEIR messages
    your_messages = [msg for msg in messages if msg['is_from_me']]
    their_messages = [msg for msg in messages if not msg['is_from_me']]

    analysis = {
        "conversation_name": conv_data.get('conversation_name', 'Unknown'),
        "total_messages": len(messages),
        "date_range": conv_data.get('date_range', 'Unknown'),
        "is_group": conv_data.get('is_group', False),

        "your_analysis": {
            "archetypes": analyze_archetypes(your_messages),
            "enneagram": analyze_enneagram(your_messages),
            "mbti": analyze_mbti(your_messages),
            "attachment_style": analyze_attachment_style(your_messages),
            "emotions": analyze_emotions(your_messages),
            "communication_patterns": analyze_communication_patterns(messages, True)
        },

        "their_analysis": {
            "archetypes": analyze_archetypes(their_messages),
            "enneagram": analyze_enneagram(their_messages),
            "mbti": analyze_mbti(their_messages),
            "attachment_style": analyze_attachment_style(their_messages),
            "emotions": analyze_emotions(their_messages),
            "communication_patterns": analyze_communication_patterns(messages, False)
        },

        "relationship_dynamics": analyze_relationship_dynamics(messages)
    }

    return analysis

def format_analysis_report(analysis):
    """Format analysis as readable text report"""

    report = []
    report.append("=" * 80)
    report.append(f"PSYCHOLOGICAL ANALYSIS: {analysis['conversation_name']}")
    report.append(f"Total Messages: {analysis['total_messages']:,}")
    report.append(f"Date Range: {analysis['date_range']}")
    report.append("=" * 80)
    report.append("")

    # YOUR ANALYSIS
    report.append("YOUR PROFILE:")
    report.append("-" * 80)

    ya = analysis['your_analysis']

    report.append(f"\n📋 Jungian Archetype: {ya['archetypes']['primary']}")
    report.append("   Top 3 Archetypes:")
    for arch in ya['archetypes']['top_three']:
        report.append(f"     - {arch['archetype']}: {arch['percentage']:.1f}%")

    report.append(f"\n🔢 Enneagram: {ya['enneagram']['likely_type']} ({ya['enneagram']['confidence']:.1f}% confidence)")

    report.append(f"\n🧠 MBTI Type: {ya['mbti']['type']}")
    for dim, data in ya['mbti']['preferences'].items():
        report.append(f"     {dim}: {data['preference']}")

    report.append(f"\n💞 Attachment Style: {ya['attachment_style']['likely_style']} ({ya['attachment_style']['confidence']:.1f}% confidence)")

    report.append(f"\n😊 Dominant Emotion: {ya['emotions']['dominant_emotion']}")

    if ya['communication_patterns']:
        cp = ya['communication_patterns']
        report.append(f"\n💬 Communication Style:")
        report.append(f"     Messages: {cp['message_count']}")
        report.append(f"     Avg Length: {cp['avg_message_length']:.0f} characters")
        report.append(f"     Questions: {cp['question_percentage']:.1f}%")
        report.append(f"     Emoji Usage: {cp['emoji_usage']:.1f}%")

    # THEIR ANALYSIS
    report.append("\n" + "=" * 80)
    report.append("THEIR PROFILE:")
    report.append("-" * 80)

    ta = analysis['their_analysis']

    report.append(f"\n📋 Jungian Archetype: {ta['archetypes']['primary']}")
    report.append("   Top 3 Archetypes:")
    for arch in ta['archetypes']['top_three']:
        report.append(f"     - {arch['archetype']}: {arch['percentage']:.1f}%")

    report.append(f"\n🔢 Enneagram: {ta['enneagram']['likely_type']} ({ta['enneagram']['confidence']:.1f}% confidence)")

    report.append(f"\n🧠 MBTI Type: {ta['mbti']['type']}")

    report.append(f"\n💞 Attachment Style: {ta['attachment_style']['likely_style']} ({ta['attachment_style']['confidence']:.1f}% confidence)")

    report.append(f"\n😊 Dominant Emotion: {ta['emotions']['dominant_emotion']}")

    if ta['communication_patterns']:
        cp = ta['communication_patterns']
        report.append(f"\n💬 Communication Style:")
        report.append(f"     Messages: {cp['message_count']}")
        report.append(f"     Avg Length: {cp['avg_message_length']:.0f} characters")
        report.append(f"     Questions: {cp['question_percentage']:.1f}%")
        report.append(f"     Emoji Usage: {cp['emoji_usage']:.1f}%")

    # RELATIONSHIP DYNAMICS
    report.append("\n" + "=" * 80)
    report.append("RELATIONSHIP DYNAMICS:")
    report.append("-" * 80)

    rd = analysis['relationship_dynamics']

    report.append(f"\n👋 Initiation:")
    report.append(f"     You initiated: {rd['initiation']['you']} conversations")
    report.append(f"     They initiated: {rd['initiation']['them']} conversations")
    report.append(f"     {rd['initiation']['who_initiates_more']} initiates more")

    report.append(f"\n⚡ Responsiveness:")
    report.append(f"     Your quick responses: {rd['responsiveness']['your_quick_responses']}")
    report.append(f"     Their quick responses: {rd['responsiveness']['their_quick_responses']}")

    report.append(f"\n⚖️  Message Balance:")
    report.append(f"     Your messages: {rd['message_balance']['you']}")
    report.append(f"     Their messages: {rd['message_balance']['them']}")
    report.append(f"     Ratio (You/Them): {rd['message_balance']['ratio']:.2f}")

    report.append("\n" + "=" * 80)

    return "\n".join(report)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python analyze_conversation.py <conversation_json_file>")
        sys.exit(1)

    json_path = sys.argv[1]

    print(f"Analyzing {json_path}...")
    analysis = analyze_conversation(json_path)

    # Save analysis JSON
    analysis_json_path = json_path.replace('.json', '_analysis.json')
    with open(analysis_json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    # Save readable report
    report = format_analysis_report(analysis)
    report_path = json_path.replace('.json', '_analysis.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✓ Analysis complete!")
    print(f"✓ JSON saved to: {analysis_json_path}")
    print(f"✓ Report saved to: {report_path}")
    print(f"\n{report}")

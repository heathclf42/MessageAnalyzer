#!/usr/bin/env python3
"""
Advanced relationship categorization: closest, most toxic, most/least reliable, etc.
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.paths import CONVERSATIONS_DIR

def calculate_closeness_score(analysis):
    """
    Calculate closeness based on:
    - Message frequency and balance
    - Emotional openness (emotion variety, vulnerability indicators)
    - Responsiveness
    - Secure attachment indicators
    """
    ya = analysis['your_analysis']
    ta = analysis['their_analysis']
    rd = analysis['relationship_dynamics']

    score = 0

    # Message balance (closer to 1.0 is better)
    ratio = rd['message_balance']['ratio']
    balance_score = 1 - abs(1 - min(ratio, 1/ratio if ratio != 0 else 0))
    score += balance_score * 20

    # Mutual responsiveness
    your_resp = rd['responsiveness']['your_quick_responses']
    their_resp = rd['responsiveness']['their_quick_responses']
    if your_resp + their_resp > 0:
        resp_score = min(your_resp, their_resp) / max(your_resp, their_resp)
        score += resp_score * 15

    # Secure attachment (both parties)
    if ya['attachment_style']['likely_style'] == 'Secure':
        score += 15
    if ta['attachment_style']['likely_style'] == 'Secure':
        score += 15

    # Emotional expression (Joy indicates positive relationship)
    if ya['emotions']['dominant_emotion'] == 'Joy':
        score += 10
    if ta['emotions']['dominant_emotion'] == 'Joy':
        score += 10

    # Message volume (normalized by time range if available)
    msg_count = analysis['total_messages']
    score += min(msg_count / 100, 15)  # Cap at 15 points

    return min(score, 100)

def calculate_toxicity_score(analysis):
    """
    Calculate toxicity based on:
    - Negative emotions (anger, sadness, fear)
    - Anxious/avoidant attachment
    - Imbalanced communication
    - Low responsiveness
    """
    ya = analysis['your_analysis']
    ta = analysis['their_analysis']
    rd = analysis['relationship_dynamics']

    score = 0

    # Negative emotions
    negative_emotions = ['Anger', 'Sadness', 'Fear']
    if ya['emotions']['dominant_emotion'] in negative_emotions:
        score += 25
    if ta['emotions']['dominant_emotion'] in negative_emotions:
        score += 25

    # Anxious or Avoidant attachment
    if ya['attachment_style']['likely_style'] in ['Anxious', 'Avoidant', 'Disorganized']:
        score += 15
    if ta['attachment_style']['likely_style'] in ['Anxious', 'Avoidant', 'Disorganized']:
        score += 15

    # Severe message imbalance (one person dominates)
    ratio = rd['message_balance']['ratio']
    if ratio > 2 or ratio < 0.5:
        score += 10

    # Poor responsiveness (one person much less responsive)
    your_resp = rd['responsiveness']['your_quick_responses']
    their_resp = rd['responsiveness']['their_quick_responses']
    if your_resp + their_resp > 0:
        resp_imbalance = abs(your_resp - their_resp) / (your_resp + their_resp)
        score += resp_imbalance * 10

    return min(score, 100)

def calculate_reliability_score(analysis):
    """
    Calculate reliability based on:
    - Consistent responsiveness
    - Message balance
    - Secure attachment
    - Supportive archetypes (Caregiver, Sage)
    """
    ya = analysis['your_analysis']
    ta = analysis['their_analysis']
    rd = analysis['relationship_dynamics']

    score = 0

    # Their responsiveness
    their_resp = rd['responsiveness']['their_quick_responses']
    score += min(their_resp / 10, 30)  # Up to 30 points

    # Secure attachment
    if ta['attachment_style']['likely_style'] == 'Secure':
        score += 25

    # Supportive archetypes
    supportive = ['Caregiver', 'Sage', 'Hero', 'Ruler']
    if ta['archetypes']['primary'] in supportive:
        score += 20

    # Consistent message balance (they participate equally)
    ratio = rd['message_balance']['ratio']
    if 0.7 <= ratio <= 1.3:
        score += 15

    # Enneagram types associated with reliability (1, 2, 6)
    reliable_types = ['Type 1 (Perfectionist)', 'Type 2 (Helper)', 'Type 6 (Loyalist)']
    if ta['enneagram']['likely_type'] in reliable_types:
        score += 10

    return min(score, 100)

def categorize_all_relationships():
    """Categorize all analyzed relationships"""

    # Load all analyses
    analysis_files = [
        f for f in os.listdir(str(CONVERSATIONS_DIR))
        if f.endswith('_analysis.json')
    ]

    scored_relationships = []

    for analysis_file in analysis_files:
        with open(str(CONVERSATIONS_DIR / analysis_file), 'r') as f:
            analysis = json.load(f)

            # Skip group chats for this analysis
            if analysis.get('is_group'):
                continue

            closeness = calculate_closeness_score(analysis)
            toxicity = calculate_toxicity_score(analysis)
            reliability = calculate_reliability_score(analysis)

            scored_relationships.append({
                'name': analysis['conversation_name'],
                'total_messages': analysis['total_messages'],
                'date_range': analysis['date_range'],
                'closeness_score': closeness,
                'toxicity_score': toxicity,
                'reliability_score': reliability,
                'your_archetype': analysis['your_analysis']['archetypes']['primary'],
                'their_archetype': analysis['their_analysis']['archetypes']['primary'],
                'your_attachment': analysis['your_analysis']['attachment_style']['likely_style'],
                'their_attachment': analysis['their_analysis']['attachment_style']['likely_style'],
                'analysis_file': analysis_file
            })

    # Sort and categorize
    categories = {
        'closest': sorted(scored_relationships, key=lambda x: x['closeness_score'], reverse=True)[:10],
        'most_toxic': sorted(scored_relationships, key=lambda x: x['toxicity_score'], reverse=True)[:10],
        'most_reliable': sorted(scored_relationships, key=lambda x: x['reliability_score'], reverse=True)[:10],
        'least_reliable': sorted(scored_relationships, key=lambda x: x['reliability_score'])[:10],
        'most_balanced': sorted(scored_relationships, key=lambda x: abs(x['closeness_score'] - 50))[:10],
    }

    # Save categorization
    output = {
        'total_relationships_analyzed': len(scored_relationships),
        'categories': categories,
        'all_relationships': scored_relationships
    }

    output_file = CONVERSATIONS_DIR / '00_RELATIONSHIP_CATEGORIES.json'
    with open(str(output_file), 'w') as f:
        json.dump(output, f, indent=2)

    # Create readable report
    report = []
    report.append("=" * 80)
    report.append("RELATIONSHIP CATEGORIZATION REPORT")
    report.append("=" * 80)
    report.append(f"\nTotal Relationships Analyzed: {len(scored_relationships)}\n")

    report.append("\n" + "=" * 80)
    report.append("🤝 YOUR CLOSEST RELATIONSHIPS")
    report.append("=" * 80)
    for i, rel in enumerate(categories['closest'], 1):
        report.append(f"\n#{i}. {rel['name']}")
        report.append(f"    Closeness Score: {rel['closeness_score']:.1f}/100")
        report.append(f"    Messages: {rel['total_messages']:,} | Range: {rel['date_range']}")
        report.append(f"    Your archetype: {rel['your_archetype']} | Their archetype: {rel['their_archetype']}")
        report.append(f"    Attachments: You={rel['your_attachment']}, Them={rel['their_attachment']}")

    report.append("\n" + "=" * 80)
    report.append("⚠️  MOST TOXIC RELATIONSHIPS")
    report.append("=" * 80)
    for i, rel in enumerate(categories['most_toxic'], 1):
        report.append(f"\n#{i}. {rel['name']}")
        report.append(f"    Toxicity Score: {rel['toxicity_score']:.1f}/100")
        report.append(f"    Messages: {rel['total_messages']:,}")
        report.append(f"    Attachments: You={rel['your_attachment']}, Them={rel['their_attachment']}")

    report.append("\n" + "=" * 80)
    report.append("✅ MOST RELIABLE PEOPLE")
    report.append("=" * 80)
    for i, rel in enumerate(categories['most_reliable'], 1):
        report.append(f"\n#{i}. {rel['name']}")
        report.append(f"    Reliability Score: {rel['reliability_score']:.1f}/100")
        report.append(f"    Their archetype: {rel['their_archetype']}")
        report.append(f"    Their attachment: {rel['their_attachment']}")

    report.append("\n" + "=" * 80)
    report.append("❌ LEAST RELIABLE PEOPLE")
    report.append("=" * 80)
    for i, rel in enumerate(categories['least_reliable'], 1):
        report.append(f"\n#{i}. {rel['name']}")
        report.append(f"    Reliability Score: {rel['reliability_score']:.1f}/100")
        report.append(f"    Messages: {rel['total_messages']:,}")

    report.append("\n" + "=" * 80)
    report.append("⚖️  MOST BALANCED RELATIONSHIPS")
    report.append("=" * 80)
    for i, rel in enumerate(categories['most_balanced'], 1):
        report.append(f"\n#{i}. {rel['name']}")
        report.append(f"    Balance Score: {rel['closeness_score']:.1f}/100")
        report.append(f"    Messages: {rel['total_messages']:,}")

    report.append("\n" + "=" * 80)

    report_file = CONVERSATIONS_DIR / '00_RELATIONSHIP_CATEGORIES.txt'
    with open(str(report_file), 'w') as f:
        f.write('\n'.join(report))

    return str(output_file), str(report_file)

if __name__ == "__main__":
    json_file, txt_file = categorize_all_relationships()

    print(f"✓ Relationship categorization complete!")
    print(f"✓ JSON data: {json_file}")
    print(f"✓ Report: {txt_file}")
    print()

    # Display report
    with open(txt_file, 'r') as f:
        print(f.read())

#!/usr/bin/env python3
"""
Enhanced analysis with citations and justifications for psychological claims.
"""

import json
import re
from collections import Counter
from analyze_conversation import (
    ARCHETYPE_KEYWORDS, ENNEAGRAM_KEYWORDS, MBTI_INDICATORS,
    ATTACHMENT_KEYWORDS, EMOTION_KEYWORDS,
    analyze_archetypes, analyze_enneagram, analyze_mbti,
    analyze_attachment_style, analyze_emotions,
    analyze_communication_patterns, analyze_relationship_dynamics
)

def find_evidence(messages, keywords_dict, top_category):
    """Find specific message examples that support the categorization"""
    evidence = []

    for msg in messages:
        text_lower = msg['text'].lower()

        # Check if message contains keywords from the top category
        if top_category in keywords_dict:
            matched_keywords = []
            for keyword in keywords_dict[top_category]:
                if keyword in text_lower:
                    matched_keywords.append(keyword)

            if matched_keywords:
                # Found evidence
                evidence.append({
                    'date': msg.get('date_formatted', 'Unknown'),
                    'text_excerpt': msg['text'][:150] + ('...' if len(msg['text']) > 150 else ''),
                    'matched_keywords': matched_keywords,
                    'is_from_me': msg['is_from_me']
                })

    # Return top 5 examples
    return evidence[:5]

def analyze_with_evidence(conversation_json_path):
    """Analyze conversation and provide evidence for claims"""

    with open(conversation_json_path, 'r', encoding='utf-8') as f:
        conv_data = json.load(f)

    messages = conv_data['messages']
    your_messages = [msg for msg in messages if msg['is_from_me']]
    their_messages = [msg for msg in messages if not msg['is_from_me']]

    # Run standard analyses
    ya_archetypes = analyze_archetypes(your_messages)
    ta_archetypes = analyze_archetypes(their_messages)
    ya_enneagram = analyze_enneagram(your_messages)
    ta_enneagram = analyze_enneagram(their_messages)
    ya_mbti = analyze_mbti(your_messages)
    ta_mbti = analyze_mbti(their_messages)
    ya_attachment = analyze_attachment_style(your_messages)
    ta_attachment = analyze_attachment_style(their_messages)
    ya_emotions = analyze_emotions(your_messages)
    ta_emotions = analyze_emotions(their_messages)
    ya_comm = analyze_communication_patterns(messages, True)
    ta_comm = analyze_communication_patterns(messages, False)
    dynamics = analyze_relationship_dynamics(messages)

    # Find evidence for each claim
    evidence = {
        "your_analysis": {
            "archetype_evidence": find_evidence(your_messages, ARCHETYPE_KEYWORDS, ya_archetypes['primary']),
            "enneagram_evidence": find_evidence(your_messages, ENNEAGRAM_KEYWORDS, ya_enneagram['likely_type']),
            "attachment_evidence": find_evidence(your_messages, ATTACHMENT_KEYWORDS, ya_attachment['likely_style']),
            "emotion_evidence": find_evidence(your_messages, EMOTION_KEYWORDS, ya_emotions['dominant_emotion'])
        },
        "their_analysis": {
            "archetype_evidence": find_evidence(their_messages, ARCHETYPE_KEYWORDS, ta_archetypes['primary']),
            "enneagram_evidence": find_evidence(their_messages, ENNEAGRAM_KEYWORDS, ta_enneagram['likely_type']),
            "attachment_evidence": find_evidence(their_messages, ATTACHMENT_KEYWORDS, ta_attachment['likely_style']),
            "emotion_evidence": find_evidence(their_messages, EMOTION_KEYWORDS, ta_emotions['dominant_emotion'])
        }
    }

    # Combine with analysis
    full_analysis = {
        "conversation_name": conv_data.get('conversation_name', 'Unknown'),
        "total_messages": len(messages),
        "date_range": conv_data.get('date_range', 'Unknown'),
        "is_group": conv_data.get('is_group', False),

        "your_analysis": {
            "archetypes": ya_archetypes,
            "enneagram": ya_enneagram,
            "mbti": ya_mbti,
            "attachment_style": ya_attachment,
            "emotions": ya_emotions,
            "communication_patterns": ya_comm
        },

        "their_analysis": {
            "archetypes": ta_archetypes,
            "enneagram": ta_enneagram,
            "mbti": ta_mbti,
            "attachment_style": ta_attachment,
            "emotions": ta_emotions,
            "communication_patterns": ta_comm
        },

        "relationship_dynamics": dynamics,
        "evidence": evidence
    }

    return full_analysis

def format_evidence_report(analysis):
    """Format analysis with evidence as readable report"""

    report = []
    report.append("=" * 80)
    report.append(f"PSYCHOLOGICAL ANALYSIS WITH EVIDENCE: {analysis['conversation_name']}")
    report.append(f"Total Messages: {analysis['total_messages']:,}")
    report.append("=" * 80)
    report.append("")

    # YOUR PROFILE WITH EVIDENCE
    report.append("YOUR PROFILE:")
    report.append("-" * 80)

    ya = analysis['your_analysis']
    ev = analysis['evidence']['your_analysis']

    report.append(f"\n📋 Primary Archetype: {ya['archetypes']['primary']}")
    report.append("\nEvidence from your messages:")
    for i, evidence in enumerate(ev['archetype_evidence'][:3], 1):
        report.append(f"  {i}. [{evidence['date']}]")
        report.append(f"     \"{evidence['text_excerpt']}\"")
        report.append(f"     Keywords: {', '.join(evidence['matched_keywords'])}")

    report.append(f"\n🔢 Enneagram Type: {ya['enneagram']['likely_type']}")
    report.append("\nEvidence:")
    for i, evidence in enumerate(ev['enneagram_evidence'][:3], 1):
        report.append(f"  {i}. [{evidence['date']}]")
        report.append(f"     \"{evidence['text_excerpt']}\"")
        report.append(f"     Keywords: {', '.join(evidence['matched_keywords'])}")

    report.append(f"\n💞 Attachment Style: {ya['attachment_style']['likely_style']}")
    report.append("\nEvidence:")
    for i, evidence in enumerate(ev['attachment_evidence'][:3], 1):
        report.append(f"  {i}. [{evidence['date']}]")
        report.append(f"     \"{evidence['text_excerpt']}\"")
        report.append(f"     Keywords: {', '.join(evidence['matched_keywords'])}")

    # THEIR PROFILE WITH EVIDENCE
    report.append("\n" + "=" * 80)
    report.append("THEIR PROFILE:")
    report.append("-" * 80)

    ta = analysis['their_analysis']
    tev = analysis['evidence']['their_analysis']

    report.append(f"\n📋 Primary Archetype: {ta['archetypes']['primary']}")
    report.append("\nEvidence from their messages:")
    for i, evidence in enumerate(tev['archetype_evidence'][:3], 1):
        report.append(f"  {i}. [{evidence['date']}]")
        report.append(f"     \"{evidence['text_excerpt']}\"")
        report.append(f"     Keywords: {', '.join(evidence['matched_keywords'])}")

    report.append(f"\n🔢 Enneagram Type: {ta['enneagram']['likely_type']}")
    report.append("\nEvidence:")
    for i, evidence in enumerate(tev['enneagram_evidence'][:3], 1):
        report.append(f"  {i}. [{evidence['date']}]")
        report.append(f"     \"{evidence['text_excerpt']}\"")
        report.append(f"     Keywords: {', '.join(evidence['matched_keywords'])}")

    report.append("\n" + "=" * 80)
    report.append("\n📊 METHODOLOGY:")
    report.append("-" * 80)
    report.append("\nArchetype Analysis:")
    report.append("  Based on Carl Jung's 12 archetypes, analyzing language patterns")
    report.append("  that indicate core personality drivers and motivations.")
    report.append("\nEnneagram Analysis:")
    report.append("  Based on Enneagram personality typing system, identifying")
    report.append("  core fears, desires, and behavioral patterns.")
    report.append("\nMBTI Analysis:")
    report.append("  Based on Myers-Briggs Type Indicator, analyzing cognitive")
    report.append("  preferences in four dimensions.")
    report.append("\nAttachment Style:")
    report.append("  Based on attachment theory (Bowlby, Ainsworth), identifying")
    report.append("  relationship patterns and emotional regulation.")

    report.append("\n" + "=" * 80)

    return "\n".join(report)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python analyze_with_evidence.py <conversation_json_file>")
        sys.exit(1)

    json_path = sys.argv[1]

    print(f"Analyzing {json_path} with evidence...")
    analysis = analyze_with_evidence(json_path)

    # Save analysis with evidence
    evidence_json_path = json_path.replace('.json', '_evidence.json')
    with open(evidence_json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)

    # Save readable report
    report = format_evidence_report(analysis)
    report_path = json_path.replace('.json', '_evidence_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✓ Analysis with evidence complete!")
    print(f"✓ JSON: {evidence_json_path}")
    print(f"✓ Report: {report_path}")
    print(f"\n{report[:2000]}...")

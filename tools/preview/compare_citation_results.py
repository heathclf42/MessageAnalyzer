#!/usr/bin/env python3
"""
Compare citation analysis results from multiple models.
Shows performance metrics and analysis quality comparison.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from citation_parser import CitationParser


def compare_models(phone_number: str = "309-948-9979"):
    """Compare citation analysis results from different models."""

    conversations_dir = Path(__file__).parent / "data" / "output" / "all_conversations"

    # Find all citation analysis files for this phone number
    citation_files = list(conversations_dir.glob(f"{phone_number}_citation_*.json"))

    if not citation_files:
        print(f"❌ No citation analysis files found for {phone_number}")
        return

    print(f"{'='*80}")
    print(f"CITATION ANALYSIS COMPARISON: {phone_number}")
    print(f"{'='*80}\n")

    parser = CitationParser()
    results = []

    for file in sorted(citation_files):
        result = parser.load_and_parse(file)
        results.append(result)

    # Performance Comparison
    print("PERFORMANCE METRICS")
    print("-" * 80)
    print(f"{'Model':<20} {'Time (min)':<12} {'Memory (MB)':<12} {'CPU %':<10} {'Response Len':<12}")
    print("-" * 80)

    for result in results:
        perf = result['metadata']['performance']
        model = result['metadata']['model']
        print(f"{model:<20} {perf['elapsed_minutes']:<12.2f} {perf['memory_mb']:<12.2f} "
              f"{perf['cpu_percent']:<10.1f} {len(result['raw_text']):<12}")

    # Citation Count Comparison
    print(f"\n\nCITATION ANALYSIS QUALITY")
    print("-" * 80)
    print(f"{'Model':<20} {'Total Citations':<16} {'Sections Found':<16} {'Avg Citations/Section':<20}")
    print("-" * 80)

    for result in results:
        parsed = result['parsed_analysis']
        model = result['metadata']['model']
        total_cites = parsed['citation_count']
        sections = parsed['sections_found']
        avg_cites = total_cites / sections if sections > 0 else 0

        print(f"{model:<20} {total_cites:<16} {sections:<16} {avg_cites:<20.1f}")

    # Per-Section Comparison
    print(f"\n\nCITATIONS BY SECTION")
    print("-" * 80)

    section_names = [
        'relationship_type',
        'communication_initiation',
        'response_patterns',
        'tone_sentiment',
        'key_topics',
        'conflict_indicators',
        'emotional_support'
    ]

    for section_name in section_names:
        print(f"\n{section_name.replace('_', ' ').title()}:")
        for result in results:
            model = result['metadata']['model']
            sections = result['parsed_analysis']['sections']

            if section_name in sections:
                data = sections[section_name]
                cites = len(data['citations'])
                conf = data.get('confidence', 'N/A')
                stats_count = len(data['statistics'])
                print(f"  {model:<20} {cites:>3} citations | Confidence: {conf:<6} | Stats: {stats_count}")
            else:
                print(f"  {model:<20} Section not found")

    # Statistics Comparison
    print(f"\n\nSTATISTICS EXTRACTED")
    print("-" * 80)

    for result in results:
        model = result['metadata']['model']
        print(f"\n{model}:")

        sections = result['parsed_analysis']['sections']
        for section_name in ['communication_initiation', 'response_patterns']:
            if section_name in sections:
                stats = sections[section_name]['statistics']
                if stats:
                    print(f"  {section_name.replace('_', ' ').title()}:")
                    for key, value in stats.items():
                        print(f"    - {key}: {value}")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compare citation analysis results")
    parser.add_argument("--phone", type=str, default="309-948-9979", help="Phone number to compare")

    args = parser.parse_args()

    compare_models(phone_number=args.phone)

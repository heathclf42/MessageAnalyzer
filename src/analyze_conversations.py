#!/usr/bin/env python3
"""
Batch analyze all conversations with psychological profiling.
"""

import os
import json
import sys
from pathlib import Path
from analyze_conversation import analyze_conversation, format_analysis_report

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.paths import CONVERSATIONS_DIR

def batch_analyze(limit=None):
    """Analyze all conversations, optionally limiting to top N"""

    # Get all JSON files (except master index and analysis files)
    json_files = sorted([
        f for f in os.listdir(str(CONVERSATIONS_DIR))
        if f.endswith('.json')
        and not f.startswith('00_')
        and not f.endswith('_analysis.json')
    ])

    if limit:
        json_files = json_files[:limit]

    print(f"Analyzing {len(json_files)} conversations...")
    print()

    analyzed_count = 0
    for i, json_file in enumerate(json_files, 1):
        json_path = str(CONVERSATIONS_DIR / json_file)

        # Skip if already analyzed
        analysis_json_path = json_path.replace('.json', '_analysis.json')
        if os.path.exists(analysis_json_path):
            print(f"[{i}/{len(json_files)}] Skipping {json_file} (already analyzed)")
            continue

        try:
            print(f"[{i}/{len(json_files)}] Analyzing {json_file}...")

            analysis = analyze_conversation(json_path)

            # Save analysis JSON
            with open(analysis_json_path, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            # Save readable report
            report = format_analysis_report(analysis)
            report_path = json_path.replace('.json', '_analysis.txt')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)

            analyzed_count += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    print()
    print(f"✓ Batch analysis complete!")
    print(f"✓ Analyzed {analyzed_count} new conversations")
    print(f"✓ Skipped {len(json_files) - analyzed_count} already analyzed")

if __name__ == "__main__":
    limit = None
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
        print(f"Limiting to top {limit} conversations")

    batch_analyze(limit)

#!/usr/bin/env python3
"""
Batch create enhanced dashboards for all analyzed conversations
"""

import os
import json
import sys
import glob
from pathlib import Path
from create_message_viewer_dashboard import create_message_viewer_dashboard

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.paths import CONVERSATIONS_DIR

def batch_create_dashboards():
    """Create enhanced dashboards for all analyzed conversations"""

    # Find all conversation JSON files (not analysis files)
    conv_files = sorted(glob.glob(str(CONVERSATIONS_DIR / '*.json')))
    # Filter out analysis, evidence, and index files
    conv_files = [f for f in conv_files if not any(x in f for x in ['_analysis.json', '_evidence.json', '00_MASTER', '00_SUMMARY'])]

    total = len(conv_files)
    print(f"Creating enhanced dashboards with evidence for {total} conversations...\n")

    for i, conv_path in enumerate(conv_files, 1):
        # Skip if dashboard already exists
        dashboard_path = conv_path.replace('.json', '_enhanced_dashboard.html')

        # Force regeneration to include evidence citations
        # if os.path.exists(dashboard_path):
        #     print(f"[{i}/{total}] Skipping {os.path.basename(conv_path)} (dashboard already exists)")
        #     continue

        print(f"[{i}/{total}] Creating dashboard for {os.path.basename(conv_path)}...")

        try:
            # Create enhanced dashboard with message viewer
            create_message_viewer_dashboard(conv_path)

        except Exception as e:
            print(f"  ✗ Error: {e}")
            continue

    print(f"\n✓ Dashboard creation complete!")

if __name__ == "__main__":
    batch_create_dashboards()

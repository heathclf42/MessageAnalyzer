#!/usr/bin/env python3
"""
Optimize dashboard UI by removing redundancy and improving information hierarchy.
Best Practices Applied:
1. Remove redundant charts (old sentiment chart replaced by weekly version)
2. Reorganize sections by importance: Weekly insights → Profiles → Messages
3. Consolidate similar visualizations
4. Improve visual hierarchy
"""

import re
from pathlib import Path


def optimize_dashboard(html_content: str) -> str:
    """Apply UI best practices to dashboard."""

    # Remove old sentiment chart (redundant with weekly version)
    # Find and remove the "Emotional Arc Over Time" section
    old_sentiment_pattern = r'<h2>💭 Emotional Arc Over Time</h2>.*?</script>\s*</div>'
    html_content = re.sub(old_sentiment_pattern, '', html_content, flags=re.DOTALL)

    print("✅ Removed redundant 'Emotional Arc Over Time' chart (replaced by weekly sentiment)")

    # Move Weekly Metrics section to the top (after header)
    # Extract weekly metrics section
    weekly_section_match = re.search(
        r'(<!-- Weekly Metrics Time-Series Section -->.*?<!-- End Weekly Metrics Section -->)',
        html_content,
        re.DOTALL
    )

    if weekly_section_match:
        weekly_section = weekly_section_match.group(1)

        # Remove from current position
        html_content = html_content.replace(weekly_section, '')

        # Insert after the Overview tab content starts (after first card div)
        # Find the Overview tab content
        overview_start = html_content.find('<div id="overview" class="tab-content active">')

        if overview_start != -1:
            # Find the first card after overview
            first_card = html_content.find('<div class="card">', overview_start)

            if first_card != -1:
                # Insert weekly section before first card
                html_content = (
                    html_content[:first_card] +
                    '\n' + weekly_section + '\n\n' +
                    html_content[first_card:]
                )

                print("✅ Moved weekly metrics to top of dashboard (primary position)")

    # Add section dividers for better visual hierarchy
    html_content = html_content.replace(
        '<h2>👤 YOUR PROFILE</h2>',
        '<hr style="margin: 40px 0; border: none; border-top: 2px solid #e0e0e0;">\n<h2>👤 YOUR PROFILE</h2>'
    )

    html_content = html_content.replace(
        '<h2>👥 THEIR PROFILE</h2>',
        '<hr style="margin: 40px 0; border: none; border-top: 2px solid #e0e0e0;">\n<h2>👥 THEIR PROFILE</h2>'
    )

    print("✅ Added visual dividers between major sections")

    # Improve weekly section title
    html_content = html_content.replace(
        '<h2 style="color: #667eea; margin-bottom: 20px;">📈 Weekly Relationship Evolution</h2>',
        '<h2 style="color: #667eea; margin-bottom: 10px; font-size: 28px;">📈 Weekly Relationship Evolution</h2>\n'
        '<p style="color: #888; font-size: 14px; margin-bottom: 20px;">Comprehensive week-by-week analysis with AI-powered insights and evidence-based metrics</p>'
    )

    print("✅ Enhanced weekly section header with descriptive subtitle")

    return html_content


def main(phone_number: str = "309-948-9979"):
    """Optimize existing dashboard UI."""

    conversations_dir = Path(__file__).parent.parent / "data" / "output" / "all_conversations"

    # Find existing dashboard
    dashboard_files = list(conversations_dir.glob(f"*{phone_number}*enhanced_dashboard.html"))

    if not dashboard_files:
        print(f"❌ No dashboard found for {phone_number}")
        return

    # Use the larger conversation file
    dashboard_file = max(dashboard_files, key=lambda f: int(f.name.split('_')[1]))

    print(f"\n🔧 Optimizing dashboard: {dashboard_file.name}")
    print("=" * 60)

    # Read existing HTML
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Apply optimizations
    optimized_html = optimize_dashboard(html_content)

    # Write back
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(optimized_html)

    print("=" * 60)
    print(f"✅ Dashboard optimized: {dashboard_file.name}")
    print(f"\n📊 UI Improvements Applied:")
    print("  • Removed redundant sentiment chart")
    print("  • Moved weekly insights to top priority position")
    print("  • Added visual section dividers")
    print("  • Improved information hierarchy")
    print(f"\n📍 File location: {dashboard_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Optimize dashboard UI")
    parser.add_argument("--phone", type=str, default="309-948-9979", help="Phone number")

    args = parser.parse_args()

    main(phone_number=args.phone)

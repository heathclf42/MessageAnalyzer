#!/usr/bin/env python3
"""
Add Stage 2 citation analysis to existing dashboards.
Edits dashboards IN PLACE - does not rename files.
"""

import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent))


def add_citation_analysis_section(html_content: str, citation_data: dict) -> str:
    """
    Add Stage 2 analysis section to existing dashboard HTML.
    Inserts before closing </body> tag.
    """

    analysis_text = citation_data.get('analysis_text', 'No analysis available')
    phone = citation_data.get('phone_number', 'Unknown')
    model = citation_data.get('model', 'Unknown')

    # Extract key sections from analysis text
    sections = {
        'Relationship Type': extract_section(analysis_text, '1. RELATIONSHIP TYPE'),
        'Communication Initiation': extract_section(analysis_text, '2. COMMUNICATION INITIATION'),
        'Response Patterns': extract_section(analysis_text, '3. RESPONSE PATTERNS'),
        'Tone and Sentiment': extract_section(analysis_text, '4. TONE AND SENTIMENT'),
        'Key Topics': extract_section(analysis_text, '5. KEY TOPICS'),
        'Conflict Indicators': extract_section(analysis_text, '6. CONFLICT INDICATORS'),
        'Emotional Support': extract_section(analysis_text, '7. EMOTIONAL SUPPORT')
    }

    # Build HTML section
    section_html = f"""
    <!-- Stage 2 LLM Analysis Section -->
    <div class="card" style="margin-top: 30px;">
        <h2 style="color: #667eea; margin-bottom: 20px;">🤖 AI Relationship Analysis</h2>
        <p style="color: #666; margin-bottom: 20px;">
            <strong>Model:</strong> {model} |
            <strong>Messages Analyzed:</strong> {citation_data.get('messages_analyzed', 0)}
        </p>

        <div style="display: flex; flex-direction: column; gap: 20px;">
"""

    for title, content in sections.items():
        if content:
            section_html += f"""
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 4px solid #667eea;">
                <h3 style="color: #667eea; margin-bottom: 10px;">{title}</h3>
                <div style="white-space: pre-wrap; line-height: 1.6; color: #333;">
                    {content[:1000]}{'...' if len(content) > 1000 else ''}
                </div>
            </div>
"""

    section_html += """
        </div>
    </div>
    <!-- End Stage 2 Analysis -->
"""

    # Insert before closing body tag
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', section_html + '\n</body>')
    else:
        html_content += section_html

    return html_content


def extract_section(text: str, section_header: str) -> str:
    """Extract a section from the analysis text."""
    if section_header not in text:
        return ""

    start = text.find(section_header)
    # Find next section header (number followed by period and uppercase)
    import re
    next_section = re.search(r'\n\n\*\*\d+\.', text[start + len(section_header):])

    if next_section:
        end = start + len(section_header) + next_section.start()
        return text[start + len(section_header):end].strip()
    else:
        return text[start + len(section_header):].strip()


def main(phone_number: str = "309-948-9979"):
    """Add citation analysis to existing dashboard."""

    conversations_dir = Path(__file__).parent.parent / "data" / "output" / "all_conversations"

    # Find citation analysis JSON
    citation_files = list(conversations_dir.glob(f"{phone_number}_citation_*.json"))
    if not citation_files:
        print(f"❌ No citation analysis found for {phone_number}")
        return

    # Use first citation file (or llama3.2 if available)
    citation_file = next((f for f in citation_files if 'llama3' in f.name), citation_files[0])

    print(f"Loading citation analysis: {citation_file.name}")
    with open(citation_file, 'r') as f:
        citation_data = json.load(f)

    # Find existing dashboard
    dashboard_files = list(conversations_dir.glob(f"*{phone_number}*dashboard.html"))
    if not dashboard_files:
        print(f"❌ No dashboard found for {phone_number}")
        return

    # Use the larger conversation file
    dashboard_file = max(dashboard_files, key=lambda f: int(f.name.split('_')[1]))

    print(f"Updating dashboard: {dashboard_file.name}")

    # Read existing HTML
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Check if already has Stage 2 analysis
    if 'Stage 2 LLM Analysis' in html_content or 'AI Relationship Analysis' in html_content:
        print("⚠️  Dashboard already has Stage 2 analysis section")
        print("Removing old section and adding new one...")
        # Remove old section
        start_marker = '<!-- Stage 2 LLM Analysis Section -->'
        end_marker = '<!-- End Stage 2 Analysis -->'
        if start_marker in html_content and end_marker in html_content:
            start = html_content.find(start_marker)
            end = html_content.find(end_marker) + len(end_marker)
            html_content = html_content[:start] + html_content[end:]

    # Add new section
    updated_html = add_citation_analysis_section(html_content, citation_data)

    # Write back to same file
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(updated_html)

    print(f"✅ Dashboard updated: {dashboard_file.name}")
    print(f"📍 File location: {dashboard_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add citation analysis to existing dashboard")
    parser.add_argument("--phone", type=str, default="309-948-9979", help="Phone number")

    args = parser.parse_args()

    main(phone_number=args.phone)

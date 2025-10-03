#!/usr/bin/env python3
"""
Add weekly metrics visualizations to existing dashboard.
Edits dashboards IN PLACE - does not rename files.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any


def parse_metrics_from_markdown(raw_analysis: str) -> Dict[str, Any]:
    """Extract numerical metrics from markdown-formatted analysis."""

    metrics = {}

    # Sentiment scores
    sentiment_match = re.search(r'\*\*YOU:\*\*.*?Positive:\s*(\d+)/100.*?Neutral:\s*(\d+)/100.*?Negative:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if sentiment_match:
        metrics['sentiment_you_pos'] = int(sentiment_match.group(1))
        metrics['sentiment_you_neg'] = int(sentiment_match.group(3))

    sentiment_them = re.search(r'\*\*THEM:\*\*.*?Positive:\s*(\d+)/100.*?Neutral:\s*(\d+)/100.*?Negative:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if sentiment_them:
        metrics['sentiment_them_pos'] = int(sentiment_them.group(1))
        metrics['sentiment_them_neg'] = int(sentiment_them.group(3))

    # Emotional States
    emotional_you = re.search(r'EMOTIONAL STATES.*?\*\*YOU:\*\*.*?Joy:\s*(\d+)/100.*?Love:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if emotional_you:
        metrics['joy_you'] = int(emotional_you.group(1))
        metrics['love_you'] = int(emotional_you.group(2))

    emotional_them = re.search(r'EMOTIONAL STATES.*?\*\*THEM:\*\*.*?Joy:\s*(\d+)/100.*?Love:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if emotional_them:
        metrics['joy_them'] = int(emotional_them.group(1))
        metrics['love_them'] = int(emotional_them.group(2))

    # Extract relationship evolution narrative
    evolution = re.search(r'RELATIONSHIP EVOLUTION\s*(.+?)(?:\n\n|Please note|\Z)', raw_analysis, re.DOTALL)
    if evolution:
        metrics['narrative'] = evolution.group(1).strip()

    return metrics


def add_weekly_section_to_dashboard(html_content: str, weekly_data: Dict[str, Any]) -> str:
    """Add weekly metrics section to existing dashboard HTML."""

    weeks = weekly_data['weekly_analyses']

    # Parse all weeks
    parsed_weeks = []
    for week in weeks:
        metrics = parse_metrics_from_markdown(week['raw_analysis'])
        metrics['week_number'] = week['week_number']
        parsed_weeks.append(metrics)

    # Prepare chart data
    week_labels = [f"Week {w['week_number'] + 1}" for w in parsed_weeks]

    sentiment_you_pos = [w.get('sentiment_you_pos', 0) for w in parsed_weeks]
    sentiment_you_neg = [w.get('sentiment_you_neg', 0) for w in parsed_weeks]
    sentiment_them_pos = [w.get('sentiment_them_pos', 0) for w in parsed_weeks]
    sentiment_them_neg = [w.get('sentiment_them_neg', 0) for w in parsed_weeks]

    joy_you = [w.get('joy_you', 0) for w in parsed_weeks]
    love_you = [w.get('love_you', 0) for w in parsed_weeks]
    joy_them = [w.get('joy_them', 0) for w in parsed_weeks]
    love_them = [w.get('love_them', 0) for w in parsed_weeks]

    # Build weekly section HTML
    section_html = f"""
    <!-- Weekly Metrics Time-Series Section -->
    <div class="card" style="margin-top: 30px;">
        <h2 style="color: #667eea; margin-bottom: 20px;">📈 Weekly Relationship Evolution</h2>
        <p style="color: #666; margin-bottom: 20px;">
            <strong>Analysis Period:</strong> {len(weeks)} weeks |
            <strong>Model:</strong> {weekly_data['model']} |
            <strong>Total Analysis Time:</strong> {weekly_data['performance_summary']['total_time_minutes']:.1f} minutes
        </p>

        <!-- Sentiment Evolution Chart -->
        <div style="margin-bottom: 40px;">
            <h3 style="color: #667eea; margin-bottom: 15px;">💬 Sentiment Over Time</h3>
            <canvas id="weeklySentimentChart" style="max-height: 400px;"></canvas>
        </div>

        <!-- Emotional Journey Chart -->
        <div style="margin-bottom: 40px;">
            <h3 style="color: #667eea; margin-bottom: 15px;">❤️ Emotional Journey</h3>
            <canvas id="weeklyEmotionalChart" style="max-height: 400px;"></canvas>
        </div>

        <!-- Weekly Narratives -->
        <div style="margin-top: 40px;">
            <h3 style="color: #667eea; margin-bottom: 15px;">📖 Weekly Analysis Narrative</h3>
"""

    for week in parsed_weeks:
        week_num = week['week_number'] + 1
        narrative = week.get('narrative', 'No analysis available for this week')

        section_html += f"""
            <div style="background: #f8f9fa; padding: 20px; margin-bottom: 15px; border-left: 4px solid #667eea; border-radius: 8px;">
                <h4 style="color: #667eea; margin-bottom: 10px;">Week {week_num}</h4>
                <p style="color: #555; line-height: 1.8;">{narrative}</p>
            </div>
"""

    section_html += """
        </div>
    </div>

    <script>
    // Weekly Sentiment Chart
    (function() {
        const ctx = document.getElementById('weeklySentimentChart');
        if (ctx) {
            new Chart(ctx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: """ + json.dumps(week_labels) + """,
                    datasets: [
                        {
                            label: 'YOU - Positive',
                            data: """ + json.dumps(sentiment_you_pos) + """,
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            borderWidth: 3,
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'THEM - Positive',
                            data: """ + json.dumps(sentiment_them_pos) + """,
                            borderColor: '#f093fb',
                            backgroundColor: 'rgba(240, 147, 251, 0.1)',
                            borderWidth: 3,
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'YOU - Negative',
                            data: """ + json.dumps(sentiment_you_neg) + """,
                            borderColor: '#ff6b6b',
                            backgroundColor: 'rgba(255, 107, 107, 0.1)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            tension: 0.4,
                            fill: false
                        },
                        {
                            label: 'THEM - Negative',
                            data: """ + json.dumps(sentiment_them_neg) + """,
                            borderColor: '#ff9999',
                            backgroundColor: 'rgba(255, 153, 153, 0.1)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            tension: 0.4,
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 2.5,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Sentiment Score (0-100)'
                            }
                        }
                    }
                }
            });
        }
    })();

    // Weekly Emotional Chart
    (function() {
        const ctx = document.getElementById('weeklyEmotionalChart');
        if (ctx) {
            new Chart(ctx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: """ + json.dumps(week_labels) + """,
                    datasets: [
                        {
                            label: 'YOU - Joy',
                            data: """ + json.dumps(joy_you) + """,
                            borderColor: '#ffd93d',
                            backgroundColor: 'rgba(255, 217, 61, 0.2)',
                            borderWidth: 3,
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'YOU - Love',
                            data: """ + json.dumps(love_you) + """,
                            borderColor: '#ff6b9d',
                            backgroundColor: 'rgba(255, 107, 157, 0.2)',
                            borderWidth: 3,
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'THEM - Joy',
                            data: """ + json.dumps(joy_them) + """,
                            borderColor: '#c7ea46',
                            backgroundColor: 'rgba(199, 234, 70, 0.2)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            tension: 0.4
                        },
                        {
                            label: 'THEM - Love',
                            data: """ + json.dumps(love_them) + """,
                            borderColor: '#ff9999',
                            backgroundColor: 'rgba(255, 153, 153, 0.2)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 2.5,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Emotional Intensity (0-100)'
                            }
                        }
                    }
                }
            });
        }
    })();
    </script>
    <!-- End Weekly Metrics Section -->
"""

    # Insert before closing body tag
    if '</body>' in html_content:
        html_content = html_content.replace('</body>', section_html + '\n</body>')
    else:
        html_content += section_html

    return html_content


def main(phone_number: str = "309-948-9979"):
    """Add weekly metrics to existing dashboard."""

    conversations_dir = Path(__file__).parent.parent / "data" / "output" / "all_conversations"

    # Find weekly metrics JSON
    weekly_files = list(conversations_dir.glob(f"{phone_number}_weekly_metrics.json"))
    if not weekly_files:
        weekly_files = list(conversations_dir.glob(f"{phone_number}_weekly_metrics_test.json"))

    if not weekly_files:
        print(f"❌ No weekly metrics found for {phone_number}")
        return

    weekly_file = weekly_files[0]

    print(f"Loading weekly metrics: {weekly_file.name}")
    with open(weekly_file, 'r') as f:
        weekly_data = json.load(f)

    # Find existing dashboard
    dashboard_files = list(conversations_dir.glob(f"*{phone_number}*enhanced_dashboard.html"))
    if not dashboard_files:
        print(f"❌ No dashboard found for {phone_number}")
        return

    # Use the larger conversation file
    dashboard_file = max(dashboard_files, key=lambda f: int(f.name.split('_')[1]))

    print(f"Updating dashboard: {dashboard_file.name}")

    # Read existing HTML
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Check if already has weekly metrics
    if 'Weekly Metrics Time-Series Section' in html_content or 'weeklySentimentChart' in html_content:
        print("⚠️  Dashboard already has weekly metrics section")
        print("Removing old section and adding new one...")
        # Remove old section
        start_marker = '<!-- Weekly Metrics Time-Series Section -->'
        end_marker = '<!-- End Weekly Metrics Section -->'
        if start_marker in html_content and end_marker in html_content:
            start = html_content.find(start_marker)
            end = html_content.find(end_marker) + len(end_marker)
            html_content = html_content[:start] + html_content[end:]

    # Add new section
    updated_html = add_weekly_section_to_dashboard(html_content, weekly_data)

    # Write back to same file
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(updated_html)

    print(f"✅ Dashboard updated: {dashboard_file.name}")
    print(f"📊 Added {len(weekly_data['weekly_analyses'])} weeks of time-series data")
    print(f"📍 File location: {dashboard_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add weekly metrics to existing dashboard")
    parser.add_argument("--phone", type=str, default="309-948-9979", help="Phone number")

    args = parser.parse_args()

    main(phone_number=args.phone)

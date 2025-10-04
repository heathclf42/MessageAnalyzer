#!/usr/bin/env python3
"""
Add weekly metrics visualizations to existing dashboard.
Edits dashboards IN PLACE - does not rename files.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any


def extract_topic_summary(raw_analysis: str) -> str:
    """Extract a concise topic/insight summary from the weekly analysis."""
    import re

    # Try to extract from TOPICS section first
    topics_match = re.search(r'#### TOPICS.*?\n\s*\d+\.\s+([^:]+):', raw_analysis, re.DOTALL)
    if topics_match:
        topic = topics_match.group(1).strip()
        return topic[:50] + '...' if len(topic) > 50 else topic

    # Fallback to relationship evolution summary (first sentence)
    evolution_match = re.search(r'RELATIONSHIP EVOLUTION\s*(.+?)(?:\.|$)', raw_analysis, re.DOTALL)
    if evolution_match:
        first_sentence = evolution_match.group(1).strip()
        # Extract up to 60 chars
        return first_sentence[:60] + '...' if len(first_sentence) > 60 else first_sentence

    return 'No summary available'


def parse_metrics_from_markdown(raw_analysis: str) -> Dict[str, Any]:
    """Extract numerical metrics from markdown-formatted analysis."""

    metrics = {}

    # Sentiment scores - handle both **YOU:** and YOU: formats, and both * and - list markers
    sentiment_match = re.search(r'(?:\*\*)?YOU(?:\*\*)?:.*?Positive:\s*(\d+)/100.*?Neutral:\s*(\d+)/100.*?Negative:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if sentiment_match:
        metrics['sentiment_you_pos'] = int(sentiment_match.group(1))
        metrics['sentiment_you_neg'] = int(sentiment_match.group(3))

    sentiment_them = re.search(r'(?:\*\*)?THEM(?:\*\*)?:.*?Positive:\s*(\d+)/100.*?Neutral:\s*(\d+)/100.*?Negative:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if sentiment_them:
        metrics['sentiment_them_pos'] = int(sentiment_them.group(1))
        metrics['sentiment_them_neg'] = int(sentiment_them.group(3))

    # Emotional States - handle both **YOU:** and YOU: formats
    emotional_you = re.search(r'EMOTIONAL STATES.*?(?:\*\*)?YOU(?:\*\*)?:.*?Joy:\s*(\d+)/100.*?Love:\s*(\d+)/100.*?Sadness:\s*(\d+)/100.*?Anger:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if emotional_you:
        metrics['joy_you'] = int(emotional_you.group(1))
        metrics['love_you'] = int(emotional_you.group(2))
        metrics['sadness_you'] = int(emotional_you.group(3))
        metrics['anger_you'] = int(emotional_you.group(4))

    emotional_them = re.search(r'EMOTIONAL STATES.*?(?:\*\*)?THEM(?:\*\*)?:.*?Joy:\s*(\d+)/100.*?Love:\s*(\d+)/100.*?Sadness:\s*(\d+)/100.*?Anger:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if emotional_them:
        metrics['joy_them'] = int(emotional_them.group(1))
        metrics['love_them'] = int(emotional_them.group(2))
        metrics['sadness_them'] = int(emotional_them.group(3))
        metrics['anger_them'] = int(emotional_them.group(4))

    # Extract relationship evolution narrative
    evolution = re.search(r'RELATIONSHIP EVOLUTION\s*(.+?)(?:\n\n|Please note|Key evidence|\Z)', raw_analysis, re.DOTALL)
    if evolution:
        metrics['narrative'] = evolution.group(1).strip()

    # Extract topic summary for tooltips
    metrics['topic_summary'] = extract_topic_summary(raw_analysis)

    return metrics


def add_weekly_section_to_dashboard(html_content: str, weekly_data: Dict[str, Any], phone_number: str, conversations_dir: Path) -> str:
    """Add weekly metrics section to existing dashboard HTML."""

    weeks = weekly_data['weekly_analyses']

    # Load conversation messages for message count and input display
    matches = list(conversations_dir.glob(f"*{phone_number}*.json"))
    matches = [f for f in matches if not any(x in f.name for x in ["_analysis", "_citation", "_weekly", "_llm"])]

    messages_by_week = {}
    if matches:
        conv_file = max(matches, key=lambda f: int(f.name.split('_')[1]))
        with open(conv_file, 'r') as f:
            conv_data = json.load(f)
            all_messages = conv_data.get('messages', [])

            # Group messages by week for the debug panel
            from datetime import datetime as dt_obj
            for msg in all_messages:
                # Handle both ISO format and standard format
                date_str = msg['date']
                try:
                    if 'T' in date_str:
                        # ISO format: 2018-12-13T11:54:12.599912
                        msg_date = dt_obj.fromisoformat(date_str.split('.')[0])
                    else:
                        # Standard format: 2018-12-13 11:54:12 AM
                        msg_date = dt_obj.strptime(date_str, '%Y-%m-%d %I:%M:%S %p')

                    week_num = (msg_date - dt_obj(msg_date.year, 1, 1)).days // 7
                    if week_num not in messages_by_week:
                        messages_by_week[week_num] = []
                    messages_by_week[week_num].append(msg)
                except Exception as e:
                    continue  # Skip messages with invalid dates

    # Parse all weeks
    parsed_weeks = []
    for week in weeks:
        metrics = parse_metrics_from_markdown(week['raw_analysis'])
        metrics['week_number'] = week['week_number']
        metrics['date_range'] = week.get('date_range', 'Unknown')
        metrics['start_date'] = week.get('start_date')
        metrics['end_date'] = week.get('end_date')
        parsed_weeks.append(metrics)

    # Prepare chart data - use date ranges if available, fallback to week numbers
    week_labels = []
    for w in parsed_weeks:
        if 'date_range' in w and w['date_range'] != 'Unknown':
            week_labels.append(w['date_range'])
        else:
            week_labels.append(f"Week {w['week_number'] + 1}")

    sentiment_you_pos = [w.get('sentiment_you_pos', 0) for w in parsed_weeks]
    sentiment_you_neg = [w.get('sentiment_you_neg', 0) for w in parsed_weeks]
    sentiment_them_pos = [w.get('sentiment_them_pos', 0) for w in parsed_weeks]
    sentiment_them_neg = [w.get('sentiment_them_neg', 0) for w in parsed_weeks]

    joy_you = [w.get('joy_you', 0) for w in parsed_weeks]
    love_you = [w.get('love_you', 0) for w in parsed_weeks]
    sadness_you = [w.get('sadness_you', 0) for w in parsed_weeks]
    anger_you = [w.get('anger_you', 0) for w in parsed_weeks]

    joy_them = [w.get('joy_them', 0) for w in parsed_weeks]
    love_them = [w.get('love_them', 0) for w in parsed_weeks]
    sadness_them = [w.get('sadness_them', 0) for w in parsed_weeks]
    anger_them = [w.get('anger_them', 0) for w in parsed_weeks]

    # Prepare topic summaries for tooltips
    week_summaries = [w.get('topic_summary', 'No summary') for w in parsed_weeks]

    # Build weekly section HTML - just the chart for top placement
    top_chart_html = f"""
                <div class="card">
                    <h2>💬 Relationship Sentiment & Emotion</h2>
                    <p style="color: #666; margin-bottom: 20px; font-size: 14px;">
                        <strong>Analysis:</strong> {len(weeks)} weeks |
                        <strong>Model:</strong> {weekly_data['model']}
                    </p>
                    <div class="chart-container">
                        <canvas id="weeklyRelationshipChart"></canvas>
                    </div>
                </div>
"""

    # Build weekly narratives section for bottom
    section_html = f"""
    <!-- Weekly Metrics Time-Series Section -->
    <div class="card" style="margin-top: 30px;">
        <h2 style="color: #667eea; margin-bottom: 20px;">📈 Weekly Analysis Details</h2>
        <p style="color: #666; margin-bottom: 20px;">
            <strong>Total weeks analyzed:</strong> {len(weeks)} |
            <strong>Analysis time:</strong> {weekly_data['performance_summary']['total_time_minutes']:.1f} minutes
        </p>

        <!-- Weekly Narratives -->
        <div>
            <h3 style="color: #667eea; margin-bottom: 15px;">📖 Weekly Analysis Narratives</h3>
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
    // Topic summaries for tooltips
    const weekSummaries = """ + json.dumps(week_summaries) + """;

    // Combined Relationship Chart (Sentiment + Emotion)
    (function() {
        const ctx = document.getElementById('weeklyRelationshipChart');
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
                            borderWidth: 2,
                            tension: 0.4,
                            fill: false
                        },
                        {
                            label: 'THEM - Positive',
                            data: """ + json.dumps(sentiment_them_pos) + """,
                            borderColor: '#f093fb',
                            backgroundColor: 'rgba(240, 147, 251, 0.1)',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: false
                        },
                        {
                            label: 'YOU - Joy',
                            data: """ + json.dumps(joy_you) + """,
                            borderColor: '#ffd93d',
                            backgroundColor: 'rgba(255, 217, 61, 0.05)',
                            borderWidth: 1.5,
                            borderDash: [2, 2],
                            tension: 0.4,
                            fill: false
                        },
                        {
                            label: 'YOU - Love',
                            data: """ + json.dumps(love_you) + """,
                            borderColor: '#ff6b9d',
                            backgroundColor: 'rgba(255, 107, 157, 0.05)',
                            borderWidth: 1.5,
                            borderDash: [2, 2],
                            tension: 0.4,
                            fill: false
                        },
                        {
                            label: 'YOU - Sadness',
                            data: """ + json.dumps(sadness_you) + """,
                            borderColor: '#4a90e2',
                            backgroundColor: 'rgba(74, 144, 226, 0.05)',
                            borderWidth: 1.5,
                            borderDash: [5, 5],
                            tension: 0.4,
                            fill: false
                        },
                        {
                            label: 'YOU - Anger',
                            data: """ + json.dumps(anger_you) + """,
                            borderColor: '#e74c3c',
                            backgroundColor: 'rgba(231, 76, 60, 0.05)',
                            borderWidth: 1.5,
                            borderDash: [5, 5],
                            tension: 0.4,
                            fill: false
                        },
                        {
                            label: 'THEM - Joy',
                            data: """ + json.dumps(joy_them) + """,
                            borderColor: '#c7ea46',
                            backgroundColor: 'rgba(199, 234, 70, 0.05)',
                            borderWidth: 1,
                            borderDash: [2, 2],
                            tension: 0.4,
                            fill: false
                        },
                        {
                            label: 'THEM - Love',
                            data: """ + json.dumps(love_them) + """,
                            borderColor: '#ff9999',
                            backgroundColor: 'rgba(255, 153, 153, 0.05)',
                            borderWidth: 1,
                            borderDash: [2, 2],
                            tension: 0.4,
                            fill: false
                        },
                        {
                            label: 'THEM - Sadness',
                            data: """ + json.dumps(sadness_them) + """,
                            borderColor: '#95b8d1',
                            backgroundColor: 'rgba(149, 184, 209, 0.05)',
                            borderWidth: 1,
                            borderDash: [5, 5],
                            tension: 0.4,
                            fill: false
                        },
                        {
                            label: 'THEM - Anger',
                            data: """ + json.dumps(anger_them) + """,
                            borderColor: '#ff7675',
                            backgroundColor: 'rgba(255, 118, 117, 0.05)',
                            borderWidth: 1,
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
                            intersect: false,
                            callbacks: {
                                title: function(context) {
                                    const index = context[0].dataIndex;
                                    const summary = weekSummaries[index];
                                    return summary || 'No summary';
                                },
                                label: function(context) {
                                    return null;  // Hide individual metric labels
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Score (0-100)'
                            }
                        }
                    }
                }
            });
        }
    })();
    </script>

    <!-- Debug Panel -->
    <div class="card" style="margin-top: 40px; background: #f8f9fa;">
        <h2 style="color: #667eea; margin-bottom: 10px; cursor: pointer;" onclick="document.getElementById('debugTable').style.display = document.getElementById('debugTable').style.display === 'none' ? 'block' : 'none'">
            🐛 Debug Panel (Click to expand)
        </h2>
        <p style="color: #666; font-size: 14px; margin-bottom: 20px;">Week-by-week validation, retries, and LLM inputs/outputs</p>

        <div id="debugTable" style="display: none;">
            <!-- Filter controls -->
            <div style="margin-bottom: 20px; padding: 15px; background: white; border-radius: 8px;">
                <label style="margin-right: 15px;">
                    <strong>Search:</strong>
                    <input type="text" id="debugFilter" onkeyup="filterDebugTable()" placeholder="Search all columns..." style="margin-left: 10px; padding: 8px; width: 300px; border: 1px solid #ddd; border-radius: 4px;">
                </label>
                <label style="margin-right: 15px;">
                    <input type="checkbox" id="filterInvalid" onchange="filterDebugTable()"> Show only invalid
                </label>
                <label style="margin-right: 15px;">
                    <input type="checkbox" id="filterRetries" onchange="filterDebugTable()"> Show only retries
                </label>
                <button onclick="document.getElementById('debugFilter').value=''; document.getElementById('filterInvalid').checked=false; document.getElementById('filterRetries').checked=false; filterDebugTable();" style="padding: 8px 15px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">Clear</button>
            </div>

            <div style="overflow-x: auto;">
                <table id="debugDataTable" style="width: 100%; border-collapse: collapse; font-size: 13px;">
                    <thead>
                        <tr style="background: #667eea; color: white;">
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Week</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Date Range</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Msg Count</th>
                            <th style="padding: 12px; text-align: center; border: 1px solid #ddd;">Valid?</th>
                            <th style="padding: 12px; text-align: center; border: 1px solid #ddd;">Retries</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Validation Errors</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Parsed Metrics</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">System Prompt</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">Input Messages</th>
                            <th style="padding: 12px; text-align: left; border: 1px solid #ddd;">LLM Response</th>
                        </tr>
                    </thead>
                    <tbody>
"""

    # Build debug table rows - use original weekly_data directly
    # We'll need to get the original messages from the conversation file
    import json as json_module

    for week_data in weekly_data['weekly_analyses']:
        week_num = week_data['week_number'] + 1
        date_range = week_data.get('date_range', 'Unknown')

        validation = week_data.get('validation', {})
        performance = week_data.get('performance', {})

        is_valid = validation.get('is_valid', False)
        errors = validation.get('errors', [])
        warnings = validation.get('warnings', [])
        retry_count = performance.get('retry_count', 0)

        # Get prompt info
        prompt_versions = performance.get('prompt_versions', [])
        final_prompt = prompt_versions[-1] if prompt_versions else {}
        system_prompt_full = final_prompt.get('system_prompt', 'N/A')

        # Get full LLM response
        raw_analysis = week_data.get('raw_analysis', '')

        # Parse metrics from the raw analysis
        parsed_metrics = parse_metrics_from_markdown(raw_analysis)
        metrics_display = f"""YOU Sentiment: {parsed_metrics.get('sentiment_you_pos', 'N/A')}/{parsed_metrics.get('sentiment_you_neg', 'N/A')}
THEM Sentiment: {parsed_metrics.get('sentiment_them_pos', 'N/A')}/{parsed_metrics.get('sentiment_them_neg', 'N/A')}
YOU Joy/Love: {parsed_metrics.get('joy_you', 'N/A')}/{parsed_metrics.get('love_you', 'N/A')}
THEM Joy/Love: {parsed_metrics.get('joy_them', 'N/A')}/{parsed_metrics.get('love_them', 'N/A')}"""

        # Get the input messages for this week
        week_messages = messages_by_week.get(week_data['week_number'], [])
        msg_count = len(week_messages)

        # Format messages for display
        if week_messages:
            messages_preview = "\\n".join([
                f"[{msg['date']}] {msg.get('sender', 'YOU' if msg.get('is_from_me') else 'THEM')}: {msg['text'][:100]}"
                for msg in week_messages[:5]
            ])
            if len(week_messages) > 5:
                messages_preview += f"\\n... and {len(week_messages) - 5} more messages"
        else:
            messages_preview = "No messages loaded"

        # Status styling
        status_color = '#28a745' if is_valid else '#dc3545'
        status_text = '✓ Valid' if is_valid else '✗ Invalid'

        # Format error list
        error_display = '<br>'.join(['• ' + e for e in errors]) if errors else '-'

        section_html += f"""
                    <tr class="debug-row" data-valid="{str(is_valid).lower()}" data-retries="{retry_count}">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Week {week_num}</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-size: 12px;">{date_range if date_range != 'Unknown' else f'Week {week_num}'}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;"><strong>{msg_count}</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: {status_color}; font-weight: bold;">{status_text}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">{retry_count}</td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-size: 11px;">
                            {error_display}
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-size: 11px; font-family: monospace; background: #fff; white-space: pre-wrap;">
                            {metrics_display.replace('<', '&lt;').replace('>', '&gt;')}
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-size: 10px; font-family: monospace; background: #fff;">
                            <details>
                                <summary style="cursor: pointer; color: #667eea;">Click to view ({len(system_prompt_full)} chars)</summary>
                                <pre style="white-space: pre-wrap; margin-top: 10px; max-height: 400px; overflow-y: auto;">{system_prompt_full.replace('<', '&lt;').replace('>', '&gt;')}</pre>
                            </details>
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-size: 10px; font-family: monospace; background: #fff;">
                            <details>
                                <summary style="cursor: pointer; color: #667eea;">Click to view ({msg_count} messages)</summary>
                                <pre style="white-space: pre-wrap; margin-top: 10px; max-height: 400px; overflow-y: auto;">{messages_preview.replace('<', '&lt;').replace('>', '&gt;')}</pre>
                            </details>
                        </td>
                        <td style="padding: 10px; border: 1px solid #ddd; font-size: 10px; font-family: monospace; background: #fff;">
                            <details>
                                <summary style="cursor: pointer; color: #667eea;">Click to view ({len(raw_analysis)} chars)</summary>
                                <pre style="white-space: pre-wrap; margin-top: 10px; max-height: 400px; overflow-y: auto;">{raw_analysis.replace('<', '&lt;').replace('>', '&gt;')}</pre>
                            </details>
                        </td>
                    </tr>
"""

    section_html += """
                </tbody>
            </table>
            </div>
        </div>

        <script>
        function filterDebugTable() {
            const searchValue = document.getElementById('debugFilter').value.toLowerCase();
            const showInvalid = document.getElementById('filterInvalid').checked;
            const showRetries = document.getElementById('filterRetries').checked;
            const rows = document.querySelectorAll('.debug-row');

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const isValid = row.dataset.valid === 'true';
                const retries = parseInt(row.dataset.retries);

                let show = true;

                // Text search
                if (searchValue && !text.includes(searchValue)) {
                    show = false;
                }

                // Invalid filter
                if (showInvalid && isValid) {
                    show = false;
                }

                // Retries filter
                if (showRetries && retries === 0) {
                    show = false;
                }

                row.style.display = show ? '' : 'none';
            });
        }
        </script>
    </div>
    <!-- End Weekly Metrics Section -->
"""

    # Replace emotional arc chart with weekly relationship chart
    emotional_arc_pattern = r'<div class="card">\s*<h2>💭 Emotional Arc Over Time</h2>.*?</div>\s*</div>'
    import re
    html_content = re.sub(emotional_arc_pattern, top_chart_html, html_content, flags=re.DOTALL)

    # Insert narratives and debug panel before closing body tag
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
    updated_html = add_weekly_section_to_dashboard(html_content, weekly_data, phone_number, conversations_dir)

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

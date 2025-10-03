#!/usr/bin/env python3
"""
Generate interactive HTML dashboard from weekly metrics analysis.
Displays time-series charts with citation tooltips and narrative insights.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any


def parse_metrics_from_markdown(raw_analysis: str) -> Dict[str, Any]:
    """Extract numerical metrics from markdown-formatted analysis."""

    metrics = {
        'sentiment': {},
        'big5': {},
        'psychological': {},
        'emotional': {},
        'archetypes': {},
        'communication': {},
        'topics': []
    }

    # Sentiment scores
    sentiment_match = re.search(r'\*\*YOU:\*\*.*?Positive:\s*(\d+)/100.*?Neutral:\s*(\d+)/100.*?Negative:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if sentiment_match:
        metrics['sentiment']['you'] = {
            'positive': int(sentiment_match.group(1)),
            'neutral': int(sentiment_match.group(2)),
            'negative': int(sentiment_match.group(3))
        }

    sentiment_them = re.search(r'\*\*THEM:\*\*.*?Positive:\s*(\d+)/100.*?Neutral:\s*(\d+)/100.*?Negative:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if sentiment_them:
        metrics['sentiment']['them'] = {
            'positive': int(sentiment_them.group(1)),
            'neutral': int(sentiment_them.group(2)),
            'negative': int(sentiment_them.group(3))
        }

    # Big 5 Personality (YOU)
    big5_you = re.search(r'PERSONALITY TRAITS.*?\*\*YOU:\*\*.*?Extroversion:\s*(\d+)/100.*?Neuroticism:\s*(\d+)/100.*?Agreeableness:\s*(\d+)/100.*?Conscientiousness:\s*(\d+)/100.*?Openness:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if big5_you:
        metrics['big5']['you'] = {
            'extroversion': int(big5_you.group(1)),
            'neuroticism': int(big5_you.group(2)),
            'agreeableness': int(big5_you.group(3)),
            'conscientiousness': int(big5_you.group(4)),
            'openness': int(big5_you.group(5))
        }

    # Big 5 (THEM)
    big5_them = re.search(r'PERSONALITY TRAITS.*?\*\*THEM:\*\*.*?Extroversion:\s*(\d+)/100.*?Neuroticism:\s*(\d+)/100.*?Agreeableness:\s*(\d+)/100.*?Conscientiousness:\s*(\d+)/100.*?Openness:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if big5_them:
        metrics['big5']['them'] = {
            'extroversion': int(big5_them.group(1)),
            'neuroticism': int(big5_them.group(2)),
            'agreeableness': int(big5_them.group(3)),
            'conscientiousness': int(big5_them.group(4)),
            'openness': int(big5_them.group(5))
        }

    # Emotional States (YOU)
    emotional_you = re.search(r'EMOTIONAL STATES.*?\*\*YOU:\*\*.*?Joy:\s*(\d+)/100.*?Love:\s*(\d+)/100.*?Sadness:\s*(\d+)/100.*?Anger:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if emotional_you:
        metrics['emotional']['you'] = {
            'joy': int(emotional_you.group(1)),
            'love': int(emotional_you.group(2)),
            'sadness': int(emotional_you.group(3)),
            'anger': int(emotional_you.group(4))
        }

    # Emotional States (THEM)
    emotional_them = re.search(r'EMOTIONAL STATES.*?\*\*THEM:\*\*.*?Joy:\s*(\d+)/100.*?Love:\s*(\d+)/100.*?Sadness:\s*(\d+)/100.*?Anger:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if emotional_them:
        metrics['emotional']['them'] = {
            'joy': int(emotional_them.group(1)),
            'love': int(emotional_them.group(2)),
            'sadness': int(emotional_them.group(3)),
            'anger': int(emotional_them.group(4))
        }

    # Psychological Traits
    psych_you = re.search(r'PSYCHOLOGICAL TRAITS.*?\*\*YOU:\*\*.*?Narcissism:\s*(\d+)/100.*?Toxicity:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if psych_you:
        metrics['psychological']['you'] = {
            'narcissism': int(psych_you.group(1)),
            'toxicity': int(psych_you.group(2))
        }

    psych_them = re.search(r'PSYCHOLOGICAL TRAITS.*?\*\*THEM:\*\*.*?Narcissism:\s*(\d+)/100.*?Toxicity:\s*(\d+)/100', raw_analysis, re.DOTALL)
    if psych_them:
        metrics['psychological']['them'] = {
            'narcissism': int(psych_them.group(1)),
            'toxicity': int(psych_them.group(2))
        }

    # Extract archetypes (YOU)
    archetype_you = re.findall(r'\*\s*(\w+):\s*(\d+)%', raw_analysis)
    if archetype_you:
        metrics['archetypes']['you'] = {arch: int(pct) for arch, pct in archetype_you[:7]}

    # Extract citations
    citations = re.findall(r'\[([^\]]+)\]\s+(?:YOU|THEM|309-948-9979):\s+"([^"]+)"\s*→\s*([^.\n]+)', raw_analysis)
    metrics['citations'] = [{'datetime': c[0], 'message': c[1], 'insight': c[2]} for c in citations]

    # Extract relationship evolution narrative
    evolution = re.search(r'RELATIONSHIP EVOLUTION\s*(.+?)(?:\n\n|\Z)', raw_analysis, re.DOTALL)
    if evolution:
        metrics['narrative'] = evolution.group(1).strip()

    return metrics


def generate_dashboard_html(weekly_data: Dict[str, Any], output_file: Path):
    """Generate interactive HTML dashboard with Chart.js visualizations."""

    phone_number = weekly_data['phone_number']
    weeks = weekly_data['weekly_analyses']

    # Parse metrics from all weeks
    parsed_weeks = []
    for week in weeks:
        week_num = week['week_number']
        raw = week['raw_analysis']
        metrics = parse_metrics_from_markdown(raw)
        metrics['week_number'] = week_num
        metrics['raw_analysis'] = raw
        parsed_weeks.append(metrics)

    # Prepare chart data
    week_labels = [f"Week {w['week_number'] + 1}" for w in parsed_weeks]

    # Sentiment over time
    sentiment_you_pos = [w['sentiment'].get('you', {}).get('positive', 0) for w in parsed_weeks]
    sentiment_you_neg = [w['sentiment'].get('you', {}).get('negative', 0) for w in parsed_weeks]
    sentiment_them_pos = [w['sentiment'].get('them', {}).get('positive', 0) for w in parsed_weeks]
    sentiment_them_neg = [w['sentiment'].get('them', {}).get('negative', 0) for w in parsed_weeks]

    # Emotional states
    joy_you = [w['emotional'].get('you', {}).get('joy', 0) for w in parsed_weeks]
    love_you = [w['emotional'].get('you', {}).get('love', 0) for w in parsed_weeks]
    joy_them = [w['emotional'].get('them', {}).get('joy', 0) for w in parsed_weeks]
    love_them = [w['emotional'].get('them', {}).get('love', 0) for w in parsed_weeks]

    # Big 5 evolution
    extroversion_you = [w['big5'].get('you', {}).get('extroversion', 0) for w in parsed_weeks]
    agreeableness_you = [w['big5'].get('you', {}).get('agreeableness', 0) for w in parsed_weeks]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Relationship Analysis - {phone_number}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-card h3 {{
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}

        .stat-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}

        .chart-container {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        .chart-container h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8em;
        }}

        .chart-wrapper {{
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }}

        .narrative-section {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}

        .narrative-section h2 {{
            color: #667eea;
            margin-bottom: 20px;
        }}

        .week-card {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
        }}

        .week-card h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}

        .week-card .narrative {{
            color: #555;
            line-height: 1.8;
            margin-bottom: 15px;
        }}

        .citations {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }}

        .citation {{
            padding: 10px;
            margin-bottom: 10px;
            background: #f0f0f0;
            border-radius: 5px;
            font-size: 0.9em;
        }}

        .citation .datetime {{
            color: #667eea;
            font-weight: bold;
        }}

        .citation .message {{
            color: #333;
            font-style: italic;
            margin: 5px 0;
        }}

        .citation .insight {{
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Weekly Relationship Analysis</h1>
            <div class="subtitle">Contact: {phone_number} | Model: {weekly_data['model']} | Analyzed: {len(weeks)} weeks</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Weeks</h3>
                <div class="value">{len(weeks)}</div>
            </div>
            <div class="stat-card">
                <h3>Analysis Time</h3>
                <div class="value">{weekly_data['performance_summary']['total_time_minutes']:.1f}<span style="font-size: 0.5em;">min</span></div>
            </div>
            <div class="stat-card">
                <h3>Avg Per Week</h3>
                <div class="value">{weekly_data['performance_summary']['average_time_per_week']:.1f}<span style="font-size: 0.5em;">sec</span></div>
            </div>
            <div class="stat-card">
                <h3>Total Output</h3>
                <div class="value">{weekly_data['performance_summary']['total_response_characters']:,}<span style="font-size: 0.5em;">chars</span></div>
            </div>
        </div>

        <div class="chart-container">
            <h2>💬 Sentiment Evolution</h2>
            <div class="chart-wrapper">
                <canvas id="sentimentChart"></canvas>
            </div>
        </div>

        <div class="chart-container">
            <h2>❤️ Emotional Journey</h2>
            <div class="chart-wrapper">
                <canvas id="emotionalChart"></canvas>
            </div>
        </div>

        <div class="chart-container">
            <h2>🧠 Personality Trends (Big 5)</h2>
            <div class="chart-wrapper">
                <canvas id="personalityChart"></canvas>
            </div>
        </div>

        <div class="narrative-section">
            <h2>📖 Weekly Narrative Analysis</h2>
"""

    # Add week cards with narratives
    for week in parsed_weeks:
        week_num = week['week_number'] + 1
        narrative = week.get('narrative', 'No narrative available')
        citations = week.get('citations', [])[:5]  # Top 5 citations

        html += f"""
            <div class="week-card">
                <h3>Week {week_num}</h3>
                <div class="narrative">{narrative}</div>

                <div class="citations">
                    <strong>Key Citations:</strong>
"""

        for citation in citations:
            html += f"""
                    <div class="citation">
                        <div class="datetime">{citation['datetime']}</div>
                        <div class="message">"{citation['message']}"</div>
                        <div class="insight">→ {citation['insight']}</div>
                    </div>
"""

        html += """
                </div>
            </div>
"""

    html += f"""
        </div>
    </div>

    <script>
        // Sentiment Chart
        const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
        new Chart(sentimentCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(week_labels)},
                datasets: [
                    {{
                        label: 'YOU - Positive',
                        data: {sentiment_you_pos},
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'THEM - Positive',
                        data: {sentiment_them_pos},
                        borderColor: '#f093fb',
                        backgroundColor: 'rgba(240, 147, 251, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'YOU - Negative',
                        data: {sentiment_you_neg},
                        borderColor: '#ff6b6b',
                        backgroundColor: 'rgba(255, 107, 107, 0.1)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        tension: 0.4,
                        fill: false
                    }},
                    {{
                        label: 'THEM - Negative',
                        data: {sentiment_them_neg},
                        borderColor: '#ff9999',
                        backgroundColor: 'rgba(255, 153, 153, 0.1)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        tension: 0.4,
                        fill: false
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }},
                    tooltip: {{
                        mode: 'index',
                        intersect: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        title: {{
                            display: true,
                            text: 'Score (0-100)'
                        }}
                    }}
                }}
            }}
        }});

        // Emotional Chart
        const emotionalCtx = document.getElementById('emotionalChart').getContext('2d');
        new Chart(emotionalCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(week_labels)},
                datasets: [
                    {{
                        label: 'YOU - Joy',
                        data: {joy_you},
                        borderColor: '#ffd93d',
                        backgroundColor: 'rgba(255, 217, 61, 0.2)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'YOU - Love',
                        data: {love_you},
                        borderColor: '#ff6b9d',
                        backgroundColor: 'rgba(255, 107, 157, 0.2)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true
                    }},
                    {{
                        label: 'THEM - Joy',
                        data: {joy_them},
                        borderColor: '#c7ea46',
                        backgroundColor: 'rgba(199, 234, 70, 0.2)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        tension: 0.4
                    }},
                    {{
                        label: 'THEM - Love',
                        data: {love_them},
                        borderColor: '#ff9999',
                        backgroundColor: 'rgba(255, 153, 153, 0.2)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        tension: 0.4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        title: {{
                            display: true,
                            text: 'Emotional Intensity (0-100)'
                        }}
                    }}
                }}
            }}
        }});

        // Personality Chart
        const personalityCtx = document.getElementById('personalityChart').getContext('2d');
        new Chart(personalityCtx, {{
            type: 'radar',
            data: {{
                labels: {json.dumps(week_labels)},
                datasets: [
                    {{
                        label: 'Extroversion',
                        data: {extroversion_you},
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.2)',
                        borderWidth: 2
                    }},
                    {{
                        label: 'Agreeableness',
                        data: {agreeableness_you},
                        borderColor: '#f093fb',
                        backgroundColor: 'rgba(240, 147, 251, 0.2)',
                        borderWidth: 2
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: 100
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Dashboard created: {output_file}")
    print(f"📊 {len(weeks)} weeks visualized")
    print(f"📍 Open in browser: file://{output_file.absolute()}")


def main(phone_number: str = "309-948-9979"):
    """Generate dashboard from weekly metrics."""

    conversations_dir = Path(__file__).parent.parent / "data" / "output" / "all_conversations"

    # Find weekly metrics file (prefer non-test version)
    weekly_files = list(conversations_dir.glob(f"{phone_number}_weekly_metrics.json"))
    if not weekly_files:
        weekly_files = list(conversations_dir.glob(f"{phone_number}_weekly_metrics_test.json"))

    if not weekly_files:
        print(f"❌ No weekly metrics found for {phone_number}")
        return

    weekly_file = weekly_files[0]

    print(f"Loading: {weekly_file.name}")

    with open(weekly_file, 'r') as f:
        weekly_data = json.load(f)

    # Generate output filename
    output_file = conversations_dir / f"{phone_number}_weekly_dashboard.html"

    generate_dashboard_html(weekly_data, output_file)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate weekly metrics dashboard")
    parser.add_argument("--phone", type=str, default="309-948-9979", help="Phone number")

    args = parser.parse_args()

    main(phone_number=args.phone)

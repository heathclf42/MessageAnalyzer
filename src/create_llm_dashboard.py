#!/usr/bin/env python3
"""
Generate interactive HTML dashboard for LLM performance metrics.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def create_llm_performance_dashboard(metrics_file: Path, output_file: Path = None):
    """Create interactive HTML dashboard from metrics JSON file.

    Args:
        metrics_file: Path to metrics JSON file
        output_file: Output HTML file path. If None, uses metrics filename.
    """

    # Load metrics
    with open(metrics_file, 'r') as f:
        data = json.load(f)

    metrics = data['metrics']
    summary = data['summary']

    if output_file is None:
        output_file = metrics_file.parent / f"{metrics_file.stem}_dashboard.html"

    # Prepare data for charts
    models = list(summary.keys())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Performance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        .timestamp {{
            color: rgba(255,255,255,0.9);
            text-align: center;
            margin-bottom: 30px;
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
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}

        .stat-unit {{
            font-size: 0.9em;
            color: #999;
            margin-left: 5px;
        }}

        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}

        .chart-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .chart-card h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3em;
        }}

        .chart-container {{
            position: relative;
            height: 300px;
        }}

        .full-width {{
            grid-column: 1 / -1;
        }}

        .metrics-table {{
            width: 100%;
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .metrics-table table {{
            width: 100%;
            border-collapse: collapse;
        }}

        .metrics-table th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .metrics-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}

        .metrics-table tr:hover {{
            background: #f5f5f5;
        }}

        .model-badge {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 LLM Performance Dashboard</h1>
        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Total Operations: {len(metrics)}
        </div>

        <!-- Summary Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Models Tested</div>
                <div class="stat-value">{len(models)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Operations</div>
                <div class="stat-value">{len(metrics)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Duration</div>
                <div class="stat-value">
                    {sum(m['duration_seconds'] for m in metrics) / len(metrics):.2f}
                    <span class="stat-unit">sec</span>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Peak Memory</div>
                <div class="stat-value">
                    {max(m['peak_memory_mb'] for m in metrics):.0f}
                    <span class="stat-unit">MB</span>
                </div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="chart-grid">
            <!-- Duration Comparison -->
            <div class="chart-card">
                <h2>⏱️ Average Duration by Model</h2>
                <div class="chart-container">
                    <canvas id="durationChart"></canvas>
                </div>
            </div>

            <!-- Memory Usage Comparison -->
            <div class="chart-card">
                <h2>💾 Peak Memory Usage by Model</h2>
                <div class="chart-container">
                    <canvas id="memoryChart"></canvas>
                </div>
            </div>

            <!-- CPU Usage Comparison -->
            <div class="chart-card">
                <h2>⚡ Average CPU Usage by Model</h2>
                <div class="chart-container">
                    <canvas id="cpuChart"></canvas>
                </div>
            </div>

            <!-- Throughput Comparison -->
            <div class="chart-card">
                <h2>📈 Throughput by Model</h2>
                <div class="chart-container">
                    <canvas id="throughputChart"></canvas>
                </div>
            </div>

            <!-- Timeline Chart -->
            <div class="chart-card full-width">
                <h2>📊 Performance Over Time</h2>
                <div class="chart-container" style="height: 400px;">
                    <canvas id="timelineChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Detailed Metrics Table -->
        <div class="metrics-table">
            <h2 style="padding: 20px; color: #333;">📋 Detailed Metrics</h2>
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Model</th>
                        <th>Operation</th>
                        <th>Text Length</th>
                        <th>Duration (s)</th>
                        <th>Memory (MB)</th>
                        <th>CPU (%)</th>
                        <th>Throughput</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f'''
                    <tr>
                        <td>{m['timestamp'].split('T')[1][:8]}</td>
                        <td><span class="model-badge">{m['model_name'].split('/')[-1][:20]}</span></td>
                        <td>{m['operation']}</td>
                        <td>{m['text_length']} chars</td>
                        <td>{m['duration_seconds']:.3f}s</td>
                        <td>{m['peak_memory_mb']:.1f} MB</td>
                        <td>{m['peak_cpu_percent']:.1f}%</td>
                        <td>{m['throughput_chars_per_sec']:.0f} c/s</td>
                    </tr>
                    ''' for m in metrics)}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Prepare data
        const summary = {json.dumps(summary)};
        const metrics = {json.dumps(metrics)};
        const models = Object.keys(summary);

        // Color palette
        const colors = [
            'rgba(102, 126, 234, 0.8)',
            'rgba(118, 75, 162, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(244, 63, 94, 0.8)',
            'rgba(251, 146, 60, 0.8)',
            'rgba(59, 130, 246, 0.8)',
        ];

        // Chart defaults
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

        // Duration Chart
        new Chart(document.getElementById('durationChart'), {{
            type: 'bar',
            data: {{
                labels: models,
                datasets: [{{
                    label: 'Avg Duration (seconds)',
                    data: models.map(m => summary[m].avg_duration_seconds),
                    backgroundColor: colors,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Seconds' }}
                    }}
                }}
            }}
        }});

        // Memory Chart
        new Chart(document.getElementById('memoryChart'), {{
            type: 'bar',
            data: {{
                labels: models,
                datasets: [{{
                    label: 'Peak Memory (MB)',
                    data: models.map(m => summary[m].max_memory_mb),
                    backgroundColor: colors,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'MB' }}
                    }}
                }}
            }}
        }});

        // CPU Chart
        new Chart(document.getElementById('cpuChart'), {{
            type: 'bar',
            data: {{
                labels: models,
                datasets: [{{
                    label: 'Avg CPU (%)',
                    data: models.map(m => summary[m].avg_cpu_percent),
                    backgroundColor: colors,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'CPU %' }}
                    }}
                }}
            }}
        }});

        // Throughput Chart
        new Chart(document.getElementById('throughputChart'), {{
            type: 'bar',
            data: {{
                labels: models,
                datasets: [{{
                    label: 'Chars/Second',
                    data: models.map(m => summary[m].avg_throughput_chars_per_sec),
                    backgroundColor: colors,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Characters/Second' }}
                    }}
                }}
            }}
        }});

        // Timeline Chart
        const modelGroups = {{}};
        metrics.forEach(m => {{
            if (!modelGroups[m.model_name]) {{
                modelGroups[m.model_name] = [];
            }}
            modelGroups[m.model_name].push(m);
        }});

        const timelineDatasets = Object.keys(modelGroups).map((model, idx) => ({{
            label: model,
            data: modelGroups[model].map((m, i) => ({{
                x: i,
                y: m.duration_seconds
            }})),
            borderColor: colors[idx % colors.length],
            backgroundColor: colors[idx % colors.length].replace('0.8', '0.2'),
            tension: 0.4
        }}));

        new Chart(document.getElementById('timelineChart'), {{
            type: 'line',
            data: {{
                datasets: timelineDatasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                    title: {{
                        display: true,
                        text: 'Duration per Operation (Sequential Order)'
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'linear',
                        title: {{ display: true, text: 'Operation Number' }}
                    }},
                    y: {{
                        beginAtZero: true,
                        title: {{ display: true, text: 'Duration (seconds)' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    with open(output_file, 'w') as f:
        f.write(html)

    return output_file


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python create_llm_dashboard.py <metrics_file.json>")
        sys.exit(1)

    metrics_file = Path(sys.argv[1])
    if not metrics_file.exists():
        print(f"Error: {metrics_file} not found")
        sys.exit(1)

    output_file = create_llm_performance_dashboard(metrics_file)
    print(f"✓ Dashboard created: {output_file}")

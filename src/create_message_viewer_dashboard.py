#!/usr/bin/env python3
"""
Create enhanced dashboards with full message viewer, search, and export capabilities.
"""

import json
import os
from datetime import datetime
from collections import defaultdict, Counter
from analyze_with_evidence import analyze_with_evidence

def analyze_timeline(messages):
    """Analyze message volume over time"""
    timeline = defaultdict(int)

    for msg in messages:
        if msg.get('date'):
            date = msg['date'][:10]  # Get YYYY-MM-DD
            timeline[date] += 1

    # Sort by date
    sorted_timeline = sorted(timeline.items())

    return {
        'dates': [item[0] for item in sorted_timeline],
        'counts': [item[1] for item in sorted_timeline]
    }

def analyze_sentiment_timeline(messages):
    """Analyze emotional arc over time"""
    # Group messages by month
    monthly_sentiment = defaultdict(lambda: {'joy': 0, 'love': 0, 'sadness': 0, 'anger': 0, 'total': 0})

    sentiment_keywords = {
        'joy': ['happy', 'great', 'amazing', 'wonderful', 'love', 'excited', 'perfect'],
        'love': ['love', 'adore', 'cherish', 'miss you', 'heart'],
        'sadness': ['sad', 'sorry', 'miss', 'hurt', 'disappointed'],
        'anger': ['angry', 'mad', 'frustrated', 'annoyed']
    }

    for msg in messages:
        if msg.get('date'):
            month = msg['date'][:7]  # Get YYYY-MM
            text_lower = msg['text'].lower()

            for sentiment, keywords in sentiment_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    monthly_sentiment[month][sentiment] += 1

            monthly_sentiment[month]['total'] += 1

    # Calculate percentages
    timeline_data = []
    for month in sorted(monthly_sentiment.keys()):
        data = monthly_sentiment[month]
        total = data['total'] or 1
        timeline_data.append({
            'month': month,
            'joy': (data['joy'] / total) * 100,
            'love': (data['love'] / total) * 100,
            'sadness': (data['sadness'] / total) * 100,
            'anger': (data['anger'] / total) * 100
        })

    return timeline_data

def create_evidence_section(evidence_list, title):
    """Create HTML for evidence citations"""
    if not evidence_list:
        return "<p><em>No evidence found</em></p>"

    html = ""
    for i, ev in enumerate(evidence_list[:5], 1):
        sender = "YOU" if ev.get('is_from_me') else "THEM"
        html += f"""
        <div class="evidence-item">
            <div class="evidence-header">
                <span class="evidence-number">#{i}</span>
                <span class="evidence-sender">{sender}</span>
                <span class="evidence-date">{ev.get('date', 'Unknown date')}</span>
            </div>
            <div class="evidence-text">"{ev.get('text_excerpt', '')}"</div>
            <div class="evidence-keywords">
                Keywords: {', '.join(ev.get('matched_keywords', []))}
            </div>
        </div>
        """
    return html

def create_message_viewer_dashboard(conv_json_path):
    """Create enhanced dashboard with full message viewer and export"""

    # Run analysis with evidence
    analysis = analyze_with_evidence(conv_json_path)

    # Load conversation for timeline and messages
    with open(conv_json_path, 'r') as f:
        conv_data = json.load(f)

    messages = conv_data['messages']
    timeline_data = analyze_timeline(messages)
    sentiment_timeline = analyze_sentiment_timeline(messages)

    conv_name = analysis['conversation_name']
    total_msgs = analysis['total_messages']
    date_range = analysis['date_range']

    ya = analysis['your_analysis']
    ta = analysis['their_analysis']
    rd = analysis['relationship_dynamics']
    ev = analysis['evidence']

    # Prepare messages for JavaScript
    messages_json = json.dumps([{
        'date': msg.get('date_formatted', 'Unknown'),
        'time': msg.get('date', '')[-8:] if msg.get('date') else '',
        'sender': 'YOU' if msg.get('is_from_me') else 'THEM',
        'text': msg.get('text', ''),
        'is_from_me': msg.get('is_from_me', False)
    } for msg in messages], ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis: {conv_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}

        .container {{
            max-width: 1800px;
            margin: 0 auto;
            width: 100%;
        }}

        header {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
        }}

        .back-btn {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }}

        .back-btn:hover {{
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}

        h1 {{
            color: #667eea;
            font-size: 36px;
            margin-bottom: 10px;
        }}

        .stats {{
            color: #666;
            font-size: 16px;
            margin-top: 15px;
        }}

        .tabs {{
            display: flex;
            gap: 10px;
            margin-top: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}

        .tab {{
            padding: 12px 24px;
            background: transparent;
            border: none;
            color: #666;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }}

        .tab:hover {{
            color: #667eea;
        }}

        .tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Split layout for analysis view */
        .split-layout {{
            display: flex;
            gap: 20px;
            margin-top: 20px;
            width: 100%;
            align-items: flex-start;
        }}

        .split-left {{
            flex: 0 0 calc(66.666% - 14px);
            min-width: 0;
        }}

        .split-right {{
            flex: 0 0 calc(33.333% - 6px);
            min-width: 0;
            position: sticky;
            top: 20px;
            max-height: calc(100vh - 200px);
            overflow-y: auto;
        }}

        .messages-panel {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .messages-panel h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .message.highlighted {{
            background: #fff3cd !important;
            border-left: 4px solid #ffc107;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin-bottom: 25px;
        }}

        .card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .card h2 {{
            color: #667eea;
            margin-bottom: 20px;
            font-size: 24px;
        }}

        .card h3 {{
            color: #764ba2;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .profile-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        .profile-item {{
            background: #f7f9fc;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}

        .profile-item strong {{
            color: #667eea;
            display: block;
            margin-bottom: 10px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .profile-item .value {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }}

        .chart-container {{
            height: 400px;
            position: relative;
            margin-top: 20px;
        }}

        .evidence-section {{
            margin-top: 20px;
        }}

        .evidence-item {{
            background: #f7f9fc;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }}

        .evidence-header {{
            display: flex;
            gap: 15px;
            margin-bottom: 10px;
            align-items: center;
        }}

        .evidence-number {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-weight: bold;
            font-size: 12px;
        }}

        .evidence-sender {{
            background: #764ba2;
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-weight: bold;
            font-size: 12px;
        }}

        .evidence-date {{
            color: #666;
            font-size: 12px;
        }}

        .evidence-text {{
            background: white;
            padding: 12px;
            border-radius: 6px;
            margin: 10px 0;
            font-style: italic;
            color: #333;
            line-height: 1.6;
        }}

        .evidence-keywords {{
            color: #667eea;
            font-size: 13px;
            font-weight: 500;
        }}

        .progress-bar {{
            background: #e0e0e0;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-fill {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: bold;
        }}

        .dynamic-row {{
            margin: 15px 0;
        }}

        .dynamic-label {{
            font-weight: 600;
            color: #555;
            margin-bottom: 5px;
        }}

        .grid .full-width {{
            grid-column: 1 / -1;
        }}

        .split-left .full-width {{
            width: 100%;
        }}

        .methodology {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }}

        .methodology h3 {{
            color: #667eea;
            margin-bottom: 10px;
        }}

        .methodology p {{
            color: #555;
            line-height: 1.6;
            margin-bottom: 10px;
        }}

        .collapsible {{
            background: #667eea;
            color: white;
            cursor: pointer;
            padding: 18px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 18px;
            font-weight: 600;
            border-radius: 10px;
            margin-top: 20px;
            transition: background 0.3s;
        }}

        .collapsible:hover {{
            background: #764ba2;
        }}

        .collapsible:after {{
            content: '\\002B';
            color: white;
            font-weight: bold;
            float: right;
            margin-left: 5px;
        }}

        .collapsible.active:after {{
            content: "\\2212";
        }}

        .collapsible-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
            background: #f7f9fc;
            border-radius: 0 0 10px 10px;
        }}

        .collapsible-content-inner {{
            padding: 20px;
            line-height: 1.8;
        }}

        .collapsible-content h4 {{
            color: #667eea;
            margin-top: 20px;
            margin-bottom: 10px;
        }}

        .collapsible-content ul {{
            margin-left: 20px;
            margin-bottom: 15px;
        }}

        .collapsible-content li {{
            margin-bottom: 8px;
        }}

        .radar-charts {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}

        .radar-chart-container {{
            height: 400px;
            position: relative;
        }}

        /* Message Viewer Styles */
        .message-controls {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: center;
        }}

        .search-box {{
            flex: 1;
            min-width: 300px;
        }}

        .search-box input {{
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}

        .search-box input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .filter-buttons {{
            display: flex;
            gap: 10px;
        }}

        .filter-btn {{
            padding: 10px 20px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
        }}

        .filter-btn:hover {{
            background: #667eea;
            color: white;
        }}

        .filter-btn.active {{
            background: #667eea;
            color: white;
        }}

        .export-buttons {{
            display: flex;
            gap: 10px;
        }}

        .export-btn {{
            padding: 10px 20px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: transform 0.2s;
        }}

        .export-btn:hover {{
            transform: translateY(-2px);
        }}

        .message-list {{
            max-height: 800px;
            overflow-y: auto;
            padding: 20px;
            background: #f7f9fc;
            border-radius: 10px;
        }}

        .message {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            animation: fadeIn 0.3s;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .message.you {{
            flex-direction: row-reverse;
        }}

        .message-avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: white;
            flex-shrink: 0;
        }}

        .message.you .message-avatar {{
            background: #667eea;
        }}

        .message.them .message-avatar {{
            background: #764ba2;
        }}

        .message-content {{
            flex: 1;
            max-width: 70%;
        }}

        .message-header {{
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 5px;
            font-size: 12px;
            color: #666;
        }}

        .message.you .message-header {{
            flex-direction: row-reverse;
        }}

        .message-sender {{
            font-weight: 600;
        }}

        .message-bubble {{
            padding: 12px 16px;
            border-radius: 18px;
            line-height: 1.5;
            word-wrap: break-word;
        }}

        .message.you .message-bubble {{
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }}

        .message.them .message-bubble {{
            background: white;
            color: #333;
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}

        .message-stats {{
            text-align: center;
            padding: 20px;
            background: #e3f2fd;
            border-radius: 10px;
            margin-bottom: 20px;
        }}

        .message-stats .count {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}

        .no-results {{
            text-align: center;
            padding: 40px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <button class="back-btn" onclick="window.location.href='00_INTERACTIVE_MASTER.html'">← Back to Dashboard</button>
            <h1>📊 {conv_name}</h1>
            <div class="stats">
                {total_msgs:,} messages | {date_range}
            </div>

        </header>

        <!-- Split Layout: Charts on Left, Messages on Right -->
        <div class="split-layout">
            <!-- Left: Charts and Analysis -->
            <div class="split-left">
                <!-- Timeline Charts -->
                <div class="card">
                    <h2>📈 Message Activity Over Time</h2>
                    <div class="chart-container">
                        <canvas id="timelineChart"></canvas>
                    </div>
                </div>

                <div class="card">
                    <h2>💭 Emotional Arc Over Time</h2>
                    <div class="chart-container">
                        <canvas id="sentimentChart"></canvas>
                    </div>
                </div>

                <!-- Psychological Profiles with Evidence -->
                <div class="grid">
                <!-- Your Profile -->
                <div class="card">
                    <h2>👤 YOUR PROFILE</h2>

                    <div class="profile-grid">
                        <div class="profile-item">
                            <strong>Primary Archetype</strong>
                            <div class="value">{ya['archetypes']['primary']}</div>
                        </div>
                        <div class="profile-item">
                            <strong>Enneagram Type</strong>
                            <div class="value">{ya['enneagram']['likely_type']}</div>
                        </div>
                        <div class="profile-item">
                            <strong>MBTI</strong>
                            <div class="value">{ya['mbti']['type']}</div>
                        </div>
                        <div class="profile-item">
                            <strong>Attachment Style</strong>
                            <div class="value">{ya['attachment_style']['likely_style']}</div>
                        </div>
                    </div>

                    <div style="margin: 15px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h3 style="margin: 0; font-size: 14px; color: #667eea;">📊 Top 7 Archetypes</h3>
                            <div style="font-size: 12px; color: #666;">
                                Primary: <strong>{ya['archetypes']['primary']}</strong>
                            </div>
                        </div>
                        <div style="height: 280px;">
                            <canvas id="yourArchetypeChart"></canvas>
                        </div>
                    </div>

                    <h3>📋 Archetype Evidence</h3>
                    <div class="evidence-section">
                        {create_evidence_section(ev['your_analysis']['archetype_evidence'], 'Archetype')}
                    </div>

                    <h3>🔢 Enneagram Evidence</h3>
                    <div class="evidence-section">
                        {create_evidence_section(ev['your_analysis']['enneagram_evidence'], 'Enneagram')}
                    </div>

                    <h3>💞 Attachment Evidence</h3>
                    <div class="evidence-section">
                        {create_evidence_section(ev['your_analysis']['attachment_evidence'], 'Attachment')}
                    </div>
                </div>

                <!-- Their Profile -->
                <div class="card">
                    <h2>👥 THEIR PROFILE</h2>

                    <div class="profile-grid">
                        <div class="profile-item">
                            <strong>Primary Archetype</strong>
                            <div class="value">{ta['archetypes']['primary']}</div>
                        </div>
                        <div class="profile-item">
                            <strong>Enneagram Type</strong>
                            <div class="value">{ta['enneagram']['likely_type']}</div>
                        </div>
                        <div class="profile-item">
                            <strong>MBTI</strong>
                            <div class="value">{ta['mbti']['type']}</div>
                        </div>
                        <div class="profile-item">
                            <strong>Attachment Style</strong>
                            <div class="value">{ta['attachment_style']['likely_style']}</div>
                        </div>
                    </div>

                    <div style="margin: 15px 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h3 style="margin: 0; font-size: 14px; color: #667eea;">📊 Top 7 Archetypes</h3>
                            <div style="font-size: 12px; color: #666;">
                                Primary: <strong>{ta['archetypes']['primary']}</strong>
                            </div>
                        </div>
                        <div style="height: 280px;">
                            <canvas id="theirArchetypeChart"></canvas>
                        </div>
                    </div>

                    <h3>📋 Archetype Evidence</h3>
                    <div class="evidence-section">
                        {create_evidence_section(ev['their_analysis']['archetype_evidence'], 'Archetype')}
                    </div>

                    <h3>🔢 Enneagram Evidence</h3>
                    <div class="evidence-section">
                        {create_evidence_section(ev['their_analysis']['enneagram_evidence'], 'Enneagram')}
                    </div>

                    <h3>💞 Attachment Evidence</h3>
                    <div class="evidence-section">
                        {create_evidence_section(ev['their_analysis']['attachment_evidence'], 'Attachment')}
                    </div>
                </div>
                </div>

                <!-- Relationship Dynamics -->
                <div class="card">
                <h2>💬 Relationship Dynamics</h2>

                <div class="dynamic-row">
                    <div class="dynamic-label">Conversation Initiation</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {(rd['initiation']['you'] / (rd['initiation']['you'] + rd['initiation']['them']) * 100):.1f}%">
                            You: {(rd['initiation']['you'] / (rd['initiation']['you'] + rd['initiation']['them']) * 100):.1f}% | Them: {(rd['initiation']['them'] / (rd['initiation']['you'] + rd['initiation']['them']) * 100):.1f}%
                        </div>
                    </div>
                    <div style="color: #666; font-size: 14px; margin-top: 5px;">You initiated {rd['initiation']['you']} conversations, they initiated {rd['initiation']['them']}</div>
                </div>

                <div class="dynamic-row">
                    <div class="dynamic-label">Quick Responses</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {(rd['responsiveness']['your_quick_responses'] / (rd['responsiveness']['your_quick_responses'] + rd['responsiveness']['their_quick_responses']) * 100):.1f}%">
                            You: {(rd['responsiveness']['your_quick_responses'] / (rd['responsiveness']['your_quick_responses'] + rd['responsiveness']['their_quick_responses']) * 100):.1f}%
                        </div>
                    </div>
                    <div style="color: #666; font-size: 14px; margin-top: 5px;">You: {rd['responsiveness']['your_quick_responses']} quick responses | Them: {rd['responsiveness']['their_quick_responses']} quick responses</div>
                </div>

                <div class="dynamic-row">
                    <div class="dynamic-label">Message Balance</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {(rd['message_balance']['you'] / (rd['message_balance']['you'] + rd['message_balance']['them']) * 100):.1f}%">
                            You: {(rd['message_balance']['you'] / (rd['message_balance']['you'] + rd['message_balance']['them']) * 100):.1f}% | Them: {(rd['message_balance']['them'] / (rd['message_balance']['you'] + rd['message_balance']['them']) * 100):.1f}%
                        </div>
                    </div>
                    <div style="color: #666; font-size: 14px; margin-top: 5px;">You: {rd['message_balance']['you']} messages | Them: {rd['message_balance']['them']} messages (Ratio: {rd['message_balance']['ratio']:.2f})</div>
                </div>

                    <div class="methodology">
                        <h3>📊 Methodology</h3>
                        <p><strong>Archetype Analysis:</strong> Based on Carl Jung's 12 archetypes, analyzing language patterns that indicate core personality drivers and motivations.</p>
                        <p><strong>Enneagram Analysis:</strong> Based on Enneagram personality typing system, identifying core fears, desires, and behavioral patterns.</p>
                        <p><strong>MBTI Analysis:</strong> Based on Myers-Briggs Type Indicator, analyzing cognitive preferences in four dimensions.</p>
                        <p><strong>Attachment Style:</strong> Based on attachment theory (Bowlby, Ainsworth), identifying relationship patterns and emotional regulation.</p>
                    </div>
                </div>
            </div> <!-- End split-left -->

            <!-- Right: Messages Panel -->
            <div class="split-right">
                <div class="messages-panel">
                    <h3>💬 Messages <span style="font-weight: normal; font-size: 14px; color: #666;">(<span id="sidebarMessageCount">{total_msgs:,}</span>)</span></h3>

                    <div class="message-controls" style="margin-bottom: 15px;">
                        <div class="search-box" style="margin-bottom: 10px;">
                            <input type="text" id="sidebarSearchInput" placeholder="🔍 Search..." onkeyup="filterSidebarMessages()" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 5px;">
                        </div>
                        <div class="filter-buttons" style="display: flex; gap: 5px; margin-bottom: 10px;">
                            <button class="filter-btn active" onclick="filterSidebarSender('all')" style="flex: 1; padding: 6px; font-size: 12px;">All</button>
                            <button class="filter-btn" onclick="filterSidebarSender('you')" style="flex: 1; padding: 6px; font-size: 12px;">You</button>
                            <button class="filter-btn" onclick="filterSidebarSender('them')" style="flex: 1; padding: 6px; font-size: 12px;">Them</button>
                        </div>
                    </div>

                    <div id="sidebarMessageList" style="max-height: calc(100vh - 400px); overflow-y: auto;">
                        <!-- Messages will be rendered here -->
                    </div>
                </div>
            </div>
        </div> <!-- End split-layout -->

        <!-- Hidden tab for backward compatibility -->
        <div id="messagesTab" class="tab-content" style="display: none;">
            <div class="card full-width">
                <h2>💬 Complete Message History</h2>

                <div class="message-controls">
                    <div class="search-box">
                        <input type="text" id="searchInput" placeholder="🔍 Search messages..." onkeyup="filterMessages()">
                    </div>

                    <div class="filter-buttons">
                        <button class="filter-btn active" onclick="filterSender('all')">All</button>
                        <button class="filter-btn" onclick="filterSender('you')">You</button>
                        <button class="filter-btn" onclick="filterSender('them')">Them</button>
                    </div>

                    <div class="export-buttons">
                        <button class="export-btn" onclick="exportJSON()">📥 Export JSON</button>
                        <button class="export-btn" onclick="exportTXT()">📄 Export TXT</button>
                    </div>
                </div>

                <div class="message-stats">
                    <span class="count" id="messageCount">{total_msgs:,}</span> messages
                    <span id="filteredInfo" style="color: #666;"></span>
                </div>

                <div class="message-list" id="messageList">
                    <!-- Messages will be inserted here by JavaScript -->
                </div>
            </div>
        </div>
    </div>

    <script>
        // Store all messages
        const allMessages = {messages_json};
        let filteredMessages = [...allMessages];
        let sidebarFilteredMessages = [...allMessages];
        let currentSenderFilter = 'all';
        let currentSearchTerm = '';
        let sidebarSenderFilter = 'all';
        let sidebarSearchTerm = '';

        // Tab switching
        function switchTab(tab) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            if (tab === 'analysis') {{
                document.querySelector('[onclick="switchTab(\\'analysis\\')"]').classList.add('active');
                document.getElementById('analysisTab').classList.add('active');
            }} else {{
                document.querySelector('[onclick="switchTab(\\'messages\\')"]').classList.add('active');
                document.getElementById('messagesTab').classList.add('active');
                renderMessages();
            }}
        }}

        // Filter by sender
        function filterSender(sender) {{
            currentSenderFilter = sender;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            applyFilters();
        }}

        // Search messages
        function filterMessages() {{
            currentSearchTerm = document.getElementById('searchInput').value.toLowerCase();
            applyFilters();
        }}

        // Apply all filters
        function applyFilters() {{
            filteredMessages = allMessages.filter(msg => {{
                // Sender filter
                if (currentSenderFilter === 'you' && msg.sender !== 'YOU') return false;
                if (currentSenderFilter === 'them' && msg.sender !== 'THEM') return false;

                // Search filter
                if (currentSearchTerm && !msg.text.toLowerCase().includes(currentSearchTerm)) return false;

                return true;
            }});

            renderMessages();
        }}

        // Render messages
        function renderMessages() {{
            console.log('renderMessages called, filteredMessages length:', filteredMessages.length);
            const messageList = document.getElementById('messageList');
            const messageCount = document.getElementById('messageCount');
            const filteredInfo = document.getElementById('filteredInfo');

            console.log('messageList element:', messageList);
            console.log('messageCount element:', messageCount);

            messageCount.textContent = filteredMessages.length.toLocaleString();

            if (filteredMessages.length < allMessages.length) {{
                filteredInfo.textContent = ` (filtered from ${{allMessages.length.toLocaleString()}})`;
            }} else {{
                filteredInfo.textContent = '';
            }}

            if (filteredMessages.length === 0) {{
                messageList.innerHTML = '<div class="no-results">No messages found matching your filters.</div>';
                return;
            }}

            messageList.innerHTML = filteredMessages.map(msg => `
                <div class="message ${{msg.is_from_me ? 'you' : 'them'}}">
                    <div class="message-avatar">${{msg.is_from_me ? 'Y' : 'T'}}</div>
                    <div class="message-content">
                        <div class="message-header">
                            <span class="message-sender">${{msg.sender}}</span>
                            <span class="message-date">${{msg.date}}</span>
                        </div>
                        <div class="message-bubble">${{msg.text.replace(/</g, '&lt;').replace(/>/g, '&gt;')}}</div>
                    </div>
                </div>
            `).join('');
        }}

        // Export functions
        function exportJSON() {{
            const dataStr = JSON.stringify(filteredMessages, null, 2);
            const dataBlob = new Blob([dataStr], {{type: 'application/json'}});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = '{conv_name}_messages.json';
            link.click();
        }}

        function exportTXT() {{
            const txtContent = filteredMessages.map(msg =>
                `[${{msg.date}}] ${{msg.sender}}: ${{msg.text}}`
            ).join('\\n\\n');

            const dataBlob = new Blob([txtContent], {{type: 'text/plain'}});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = '{conv_name}_messages.txt';
            link.click();
        }}

        // Sidebar message functions
        function filterSidebarSender(sender) {{
            sidebarSenderFilter = sender;
            document.querySelectorAll('.split-right .filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            applySidebarFilters();
        }}

        function filterSidebarMessages() {{
            sidebarSearchTerm = document.getElementById('sidebarSearchInput').value.toLowerCase();
            applySidebarFilters();
        }}

        function applySidebarFilters() {{
            sidebarFilteredMessages = allMessages.filter(msg => {{
                if (sidebarSenderFilter === 'you' && msg.sender !== 'YOU') return false;
                if (sidebarSenderFilter === 'them' && msg.sender === 'YOU') return false;
                if (sidebarSearchTerm && !msg.text.toLowerCase().includes(sidebarSearchTerm)) return false;
                return true;
            }});
            renderSidebarMessages();
        }}

        function renderSidebarMessages() {{
            const sidebarList = document.getElementById('sidebarMessageList');
            const sidebarCount = document.getElementById('sidebarMessageCount');

            sidebarCount.textContent = sidebarFilteredMessages.length.toLocaleString();

            if (sidebarFilteredMessages.length === 0) {{
                sidebarList.innerHTML = '<div style="text-align: center; color: #999; padding: 20px;">No messages found</div>';
                return;
            }}

            sidebarList.innerHTML = sidebarFilteredMessages.map((msg, idx) => `
                <div class="message ${{msg.is_from_me ? 'you' : 'them'}}" id="msg-${{idx}}" style="margin-bottom: 10px; padding: 10px; border-radius: 8px; cursor: default;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span style="font-weight: bold; font-size: 12px;">${{msg.sender}}</span>
                        <span style="font-size: 11px; color: #999;">${{msg.date ? msg.date.substring(0, 10) : ''}}</span>
                    </div>
                    <div style="font-size: 13px; line-height: 1.4;">${{msg.text.substring(0, 150)}}${{msg.text.length > 150 ? '...' : ''}}</div>
                </div>
            `).join('');
        }}

        function filterMessagesByDate(dateStr) {{
            sidebarSearchTerm = '';
            document.getElementById('sidebarSearchInput').value = '';
            sidebarFilteredMessages = allMessages.filter(msg => msg.date && msg.date.startsWith(dateStr));
            renderSidebarMessages();

            // Scroll sidebar to top
            document.getElementById('sidebarMessageList').scrollTop = 0;
        }}

        function filterMessagesByMonth(monthStr) {{
            sidebarSearchTerm = '';
            document.getElementById('sidebarSearchInput').value = '';
            sidebarFilteredMessages = allMessages.filter(msg => msg.date && msg.date.substring(0, 7) === monthStr);
            renderSidebarMessages();

            // Scroll sidebar to top
            document.getElementById('sidebarMessageList').scrollTop = 0;
        }}

        // Timeline Chart
        const timelineCtx = document.getElementById('timelineChart').getContext('2d');
        new Chart(timelineCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(timeline_data['dates'])},
                datasets: [{{
                    label: 'Messages per Day',
                    data: {json.dumps(timeline_data['counts'])},
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        type: 'time',
                        time: {{
                            unit: 'month'
                        }}
                    }},
                    y: {{
                        beginAtZero: true
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                onClick: (event, elements) => {{
                    if (elements.length > 0) {{
                        const index = elements[0].index;
                        const dateStr = {json.dumps(timeline_data['dates'])}[index];
                        filterMessagesByDate(dateStr);
                    }}
                }}
            }}
        }});

        // Sentiment Chart
        const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
        new Chart(sentimentCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps([s['month'] for s in sentiment_timeline])},
                datasets: [
                    {{
                        label: 'Joy',
                        data: {json.dumps([s['joy'] for s in sentiment_timeline])},
                        borderColor: '#ffd700',
                        backgroundColor: 'rgba(255, 215, 0, 0.1)',
                        tension: 0.4
                    }},
                    {{
                        label: 'Love',
                        data: {json.dumps([s['love'] for s in sentiment_timeline])},
                        borderColor: '#ff69b4',
                        backgroundColor: 'rgba(255, 105, 180, 0.1)',
                        tension: 0.4
                    }},
                    {{
                        label: 'Sadness',
                        data: {json.dumps([s['sadness'] for s in sentiment_timeline])},
                        borderColor: '#4682b4',
                        backgroundColor: 'rgba(70, 130, 180, 0.1)',
                        tension: 0.4
                    }},
                    {{
                        label: 'Anger',
                        data: {json.dumps([s['anger'] for s in sentiment_timeline])},
                        borderColor: '#dc143c',
                        backgroundColor: 'rgba(220, 20, 60, 0.1)',
                        tension: 0.4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        type: 'time',
                        time: {{
                            unit: 'month'
                        }}
                    }},
                    y: {{
                        beginAtZero: true,
                        max: 100,
                        ticks: {{
                            callback: function(value) {{
                                return value + '%';
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }},
                onClick: (event, elements) => {{
                    if (elements.length > 0) {{
                        const index = elements[0].index;
                        const monthStr = {json.dumps([s['month'] for s in sentiment_timeline])}[index];
                        filterMessagesByMonth(monthStr);
                    }}
                }}
            }}
        }});

        // Prepare archetype data (top 7)
        const yourArchetypes = {json.dumps(ya['archetypes']['scores'])};
        const theirArchetypes = {json.dumps(ta['archetypes']['scores'])};

        // Get top 7 archetypes for each person
        const getTop7 = (scores) => {{
            return Object.entries(scores)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 7);
        }};

        const yourTop7 = getTop7(yourArchetypes);
        const theirTop7 = getTop7(theirArchetypes);

        // Your Archetype Radar Chart
        const yourArchetypeCtx = document.getElementById('yourArchetypeChart').getContext('2d');
        new Chart(yourArchetypeCtx, {{
            type: 'radar',
            data: {{
                labels: yourTop7.map(([name, _]) => name),
                datasets: [{{
                    label: 'Your Archetypes',
                    data: yourTop7.map(([_, score]) => score),
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(59, 130, 246, 1)'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: Math.max(...yourTop7.map(([_, score]) => score)) * 1.1,
                        ticks: {{
                            stepSize: 2,
                            callback: function(value) {{
                                return value.toFixed(1);
                            }}
                        }},
                        pointLabels: {{
                            font: {{
                                size: 11
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.label + ': ' + context.parsed.r.toFixed(1) + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Their Archetype Radar Chart
        const theirArchetypeCtx = document.getElementById('theirArchetypeChart').getContext('2d');
        new Chart(theirArchetypeCtx, {{
            type: 'radar',
            data: {{
                labels: theirTop7.map(([name, _]) => name),
                datasets: [{{
                    label: 'Their Archetypes',
                    data: theirTop7.map(([_, score]) => score),
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(16, 185, 129, 1)',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: 'rgba(16, 185, 129, 1)'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        max: Math.max(...theirTop7.map(([_, score]) => score)) * 1.1,
                        ticks: {{
                            stepSize: 2,
                            callback: function(value) {{
                                return value.toFixed(1);
                            }}
                        }},
                        pointLabels: {{
                            font: {{
                                size: 11
                            }}
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.label + ': ' + context.parsed.r.toFixed(1) + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Initialize messages on page load
        window.addEventListener('DOMContentLoaded', function() {{
            console.log('Page loaded, initializing messages...');
            // Render sidebar messages immediately
            renderSidebarMessages();
            // Pre-render messages for legacy tab
            renderMessages();
        }});
    </script>
</body>
</html>
"""

    # Save dashboard
    output_path = conv_json_path.replace('.json', '_enhanced_dashboard.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python create_message_viewer_dashboard.py <conversation_json_file>")
        sys.exit(1)

    json_path = sys.argv[1]
    output = create_message_viewer_dashboard(json_path)
    print(f"✓ Enhanced dashboard with message viewer created: {output}")

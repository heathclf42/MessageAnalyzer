#!/usr/bin/env python3
"""
Create interactive master dashboard with adjustable filters and controls.
"""

import json
import os
import sys
from pathlib import Path
from collections import Counter

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.paths import CONVERSATIONS_DIR

def create_interactive_master():
    """Create interactive master dashboard with controls"""

    # Load all analysis files
    analysis_files = [
        f for f in os.listdir(str(CONVERSATIONS_DIR))
        if f.endswith('_analysis.json')
    ]

    all_analyses = []
    for analysis_file in analysis_files:
        with open(str(CONVERSATIONS_DIR / analysis_file), 'r') as f:
            analysis = json.load(f)
            # Add filename for dashboard links
            analysis['filename'] = analysis_file.replace('_analysis.json', '')
            all_analyses.append(analysis)

    # Load relationship scores from categorization file
    scores_path = CONVERSATIONS_DIR / '00_RELATIONSHIP_CATEGORIES.json'
    relationship_scores = {}
    if scores_path.exists():
        with open(scores_path, 'r') as f:
            categories = json.load(f)
            # Load from 'all_relationships' list
            if 'all_relationships' in categories:
                for conv in categories['all_relationships']:
                    name = conv.get('name', conv.get('conversation_name', ''))
                    if name:
                        relationship_scores[name] = {
                            'closeness_score': conv.get('closeness_score', 0),
                            'toxicity_score': conv.get('toxicity_score', 0),
                            'reliability_score': conv.get('reliability_score', 0)
                        }

    # Aggregate statistics
    total_messages = sum(a['total_messages'] for a in all_analyses)
    total_conversations = len(all_analyses)

    # Archetype distribution
    your_archetypes = Counter()
    their_archetypes = Counter()

    for analysis in all_analyses:
        your_archetypes[analysis['your_analysis']['archetypes']['primary']] += 1
        their_archetypes[analysis['their_analysis']['archetypes']['primary']] += 1

    # Sort all conversations by message count
    sorted_convs = sorted(all_analyses, key=lambda x: x['total_messages'], reverse=True)

    # Convert to JSON for JavaScript
    convs_json = json.dumps([{
        'name': c['conversation_name'],
        'filename': c['filename'],
        'total_messages': c['total_messages'],
        'date_range': c['date_range'],
        'your_archetype': c['your_analysis']['archetypes']['primary'],
        'their_archetype': c['their_analysis']['archetypes']['primary'],
        'is_group': c.get('is_group', False),
        'your_messages': c['relationship_dynamics']['message_balance']['you'],
        'their_messages': c['relationship_dynamics']['message_balance']['them'],
        'you_initiate': c['relationship_dynamics']['initiation']['you'],
        'they_initiate': c['relationship_dynamics']['initiation']['them'],
        'closeness_score': relationship_scores.get(c['conversation_name'], {}).get('closeness_score', 0),
        'toxicity_score': relationship_scores.get(c['conversation_name'], {}).get('toxicity_score', 0),
        'reliability_score': relationship_scores.get(c['conversation_name'], {}).get('reliability_score', 0)
    } for c in sorted_convs])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Master Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
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
            color: #333;
            padding: 20px;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            padding: 40px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }}

        h1 {{
            color: #667eea;
            font-size: 48px;
            margin-bottom: 20px;
        }}

        .stats-row {{
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 30px;
        }}

        .stat-box {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 25px;
            border-radius: 15px;
            min-width: 200px;
            text-align: center;
        }}

        .stat-number {{
            font-size: 48px;
            font-weight: bold;
        }}

        .stat-label {{
            margin-top: 10px;
            opacity: 0.9;
        }}

        .controls {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .control-group {{
            margin: 20px 0;
        }}

        .control-group label {{
            display: block;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}

        .slider-container {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        .slider {{
            flex: 1;
            height: 8px;
            border-radius: 5px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
        }}

        .slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
        }}

        .slider::-moz-range-thumb {{
            width: 25px;
            height: 25px;
            border-radius: 50%;
            background: #667eea;
            cursor: pointer;
        }}

        .slider-value {{
            min-width: 100px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
        }}

        .preset-buttons {{
            display: flex;
            gap: 10px;
            margin-top: 15px;
        }}

        .preset-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }}

        .preset-btn:hover {{
            background: #764ba2;
            transform: translateY(-2px);
        }}

        .card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 25px;
        }}

        .card h2 {{
            color: #667eea;
            margin-bottom: 20px;
        }}

        #network {{
            width: 100%;
            min-height: 400px;
            max-height: 1200px;
            background: #f5f7fa;
            border-radius: 15px;
        }}

        .conversation-list {{
            max-height: 600px;
            overflow-y: auto;
        }}

        .conv-item {{
            background: #f7f9fc;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: transform 0.2s;
            cursor: pointer;
        }}

        .conv-item:hover {{
            transform: translateX(5px);
            background: #e3f2fd;
        }}

        .conv-name {{
            font-weight: bold;
            color: #667eea;
        }}

        .conv-stats {{
            color: #666;
            font-size: 14px;
        }}

        /* Tooltip styling */
        .network-tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.2s;
            font-size: 13px;
            line-height: 1.6;
            max-width: 300px;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}

        .network-tooltip.visible {{
            opacity: 1;
        }}

        .network-tooltip strong {{
            display: block;
            font-size: 14px;
            margin-bottom: 6px;
            color: #ffd700;
        }}

        /* Node hover effect */
        .node-group:hover circle {{
            stroke-width: 4;
            filter: brightness(1.2);
        }}

        .chart-container {{
            height: 400px;
            position: relative;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin-bottom: 25px;
        }}

        .full-width {{
            grid-column: 1 / -1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 Your Communication Universe</h1>
            <p style="font-size: 18px; color: #666; margin-top: 10px;">
                Interactive exploration of all your conversations
            </p>

            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-number">{total_conversations}</div>
                    <div class="stat-label">Total Conversations</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number">{total_messages:,}</div>
                    <div class="stat-label">Total Messages</div>
                </div>
                <div class="stat-box" id="filteredBox" style="display: none;">
                    <div class="stat-number" id="filteredCount">{total_conversations}</div>
                    <div class="stat-label">Filtered</div>
                </div>
                <div class="stat-box">
                    <div class="stat-number" id="displayedCount">20</div>
                    <div class="stat-label">Currently Showing</div>
                </div>
            </div>
        </header>

        <!-- Controls -->
        <div class="controls">
            <h2 style="color: #667eea; margin-bottom: 20px;">🎛️ Display Controls</h2>

            <div class="control-group">
                <label>Number of Conversations to Display:</label>
                <div class="slider-container">
                    <input type="range" min="5" max="{total_conversations}" value="20" class="slider" id="convSlider">
                    <div class="slider-value" id="sliderValue">20</div>
                </div>
                <div class="preset-buttons">
                    <button class="preset-btn" onclick="setConversations(5)">Top 5</button>
                    <button class="preset-btn" onclick="setConversations(10)">Top 10</button>
                    <button class="preset-btn" onclick="setConversations(50)">Top 50</button>
                    <button class="preset-btn" onclick="setConversations(200)">Top 200</button>
                    <button class="preset-btn" onclick="setConversations(400)">Top 400</button>
                    <button class="preset-btn" onclick="setConversations({total_conversations})">All</button>
                </div>
            </div>

        </div>

        <!-- Network Graph -->
        <div class="card">
            <h2 id="networkHeading">🕸️ Relationship Network (sorted by message count)</h2>
            <div class="network-tooltip" id="networkTooltip"></div>

            <div style="margin-bottom: 20px;">
                <div style="display: inline-block; margin-right: 20px;">
                    <label style="font-weight: bold; color: #667eea; margin-right: 10px;">Search:</label>
                    <input type="text" id="networkSearch" placeholder="Search by name or number..." onkeyup="searchNetwork()" style="padding: 10px 20px; border: 2px solid #667eea; border-radius: 20px; font-size: 14px; width: 300px;">
                </div>

                <div style="display: inline-block;">
                    <label style="font-weight: bold; color: #667eea; margin-right: 10px;">Sort by:</label>
                    <select id="networkSortSelect" onchange="sortAndUpdateNetwork(this.value)" style="padding: 10px 20px; border: 2px solid #667eea; border-radius: 20px; font-size: 14px; background: white; color: #667eea; cursor: pointer;">
                        <option value="message_count">Message Count (Most to Least)</option>
                        <option value="recent">Most Recent Activity</option>
                        <option value="oldest">Oldest First</option>
                        <option value="duration">Longest Relationship</option>
                        <option value="balanced">Most Balanced</option>
                        <option value="least_balanced">Least Balanced</option>
                        <option value="closest">Closest Relationships</option>
                        <option value="most_toxic">Most Toxic</option>
                        <option value="least_toxic">Least Toxic</option>
                        <option value="most_reliable">Most Reliable</option>
                        <option value="least_reliable">Least Reliable</option>
                        <option value="your_initiation">You Initiate Most</option>
                        <option value="their_initiation">They Initiate Most</option>
                        <option value="alphabetical">Alphabetical</option>
                    </select>
                </div>
            </div>

            <svg id="network"></svg>
        </div>

        <!-- Archetype Distribution -->
        <div class="card full-width">
            <h2>📋 Archetype Distribution: You, Them</h2>
            <div class="chart-container" style="height: 500px;">
                <canvas id="archetypesChart"></canvas>
            </div>
        </div>

        <!-- Conversation List -->
        <div class="card">
            <h2 id="conversationHeading">📊 Conversations (sorted by message count)</h2>

            <div style="margin-bottom: 20px;">
                <div style="display: inline-block; margin-right: 20px;">
                    <label style="font-weight: bold; color: #667eea; margin-right: 10px;">Filter by Type:</label>
                    <button class="preset-btn" onclick="filterConversations('all')" style="margin: 0 5px;">All</button>
                    <button class="preset-btn" onclick="filterConversations('individual')" style="margin: 0 5px;">1-on-1 Only</button>
                    <button class="preset-btn" onclick="filterConversations('group')" style="margin: 0 5px;">Groups Only</button>
                </div>

                <div style="display: inline-block;">
                    <label style="font-weight: bold; color: #667eea; margin-right: 10px;">Sort by:</label>
                    <select id="sortSelect" onchange="sortConversations(this.value)" style="padding: 10px 20px; border: 2px solid #667eea; border-radius: 20px; font-size: 14px; background: white; color: #667eea; cursor: pointer;">
                        <option value="message_count">Message Count (Most to Least)</option>
                        <option value="recent">Most Recent Activity</option>
                        <option value="oldest">Oldest First</option>
                        <option value="duration">Longest Relationship</option>
                        <option value="balanced">Most Balanced</option>
                        <option value="least_balanced">Least Balanced</option>
                        <option value="closest">Closest Relationships</option>
                        <option value="most_toxic">Most Toxic</option>
                        <option value="least_toxic">Least Toxic</option>
                        <option value="most_reliable">Most Reliable</option>
                        <option value="least_reliable">Least Reliable</option>
                        <option value="your_initiation">You Initiate Most</option>
                        <option value="their_initiation">They Initiate Most</option>
                        <option value="alphabetical">Alphabetical</option>
                    </select>
                </div>
            </div>

            <div class="conversation-list" id="conversationList"></div>
        </div>
    </div>

    <script>
        // Data
        const allConversations = {convs_json};
        let filteredConversations = [...allConversations];
        let displayLimit = 20;

        // Slider control
        const slider = document.getElementById('convSlider');
        const sliderValue = document.getElementById('sliderValue');
        const displayedCount = document.getElementById('displayedCount');
        const filteredCount = document.getElementById('filteredCount');
        const filteredBox = document.getElementById('filteredBox');
        let currentFilter = 'all';

        slider.addEventListener('input', function() {{
            displayLimit = parseInt(this.value);
            sliderValue.textContent = displayLimit === {total_conversations} ? 'All' : displayLimit;
            updateDisplay();
        }});

        function setConversations(num) {{
            displayLimit = num;
            slider.value = num;
            sliderValue.textContent = num === {total_conversations} ? 'All' : num;
            updateDisplay();
        }}

        function filterConversations(type) {{
            currentFilter = type;
            if (type === 'all') {{
                filteredConversations = [...allConversations];
            }} else if (type === 'individual') {{
                filteredConversations = allConversations.filter(c => !c.is_group);
            }} else if (type === 'group') {{
                filteredConversations = allConversations.filter(c => c.is_group);
            }}

            // Re-apply current sort
            const sortValue = document.getElementById('sortSelect').value;
            sortConversations(sortValue, false);
        }}

        function sortConversations(sortBy, updateAfter = true) {{
            const sortLabels = {{
                'message_count': 'Message Count (Most to Least)',
                'recent': 'Most Recent Activity',
                'oldest': 'Oldest First',
                'duration': 'Longest Relationship',
                'balanced': 'Most Balanced',
                'least_balanced': 'Least Balanced',
                'closest': 'Closest Relationships',
                'most_toxic': 'Most Toxic',
                'least_toxic': 'Least Toxic',
                'most_reliable': 'Most Reliable',
                'least_reliable': 'Least Reliable',
                'your_initiation': 'You Initiate Most',
                'their_initiation': 'They Initiate Most',
                'alphabetical': 'Alphabetical'
            }};

            // Update heading
            document.getElementById('conversationHeading').textContent = `📊 Conversations (sorted by ${{sortLabels[sortBy] || sortBy}})`;

            switch(sortBy) {{
                case 'message_count':
                    filteredConversations.sort((a, b) => b.total_messages - a.total_messages);
                    break;
                case 'recent':
                    filteredConversations.sort((a, b) => {{
                        const dateA = new Date(a.date_range.split(' to ')[1]);
                        const dateB = new Date(b.date_range.split(' to ')[1]);
                        return dateB - dateA;
                    }});
                    break;
                case 'oldest':
                    filteredConversations.sort((a, b) => {{
                        const dateA = new Date(a.date_range.split(' to ')[0]);
                        const dateB = new Date(b.date_range.split(' to ')[0]);
                        return dateA - dateB;
                    }});
                    break;
                case 'duration':
                    filteredConversations.sort((a, b) => {{
                        const durationA = new Date(a.date_range.split(' to ')[1]) - new Date(a.date_range.split(' to ')[0]);
                        const durationB = new Date(b.date_range.split(' to ')[1]) - new Date(b.date_range.split(' to ')[0]);
                        return durationB - durationA;
                    }});
                    break;
                case 'balanced':
                    filteredConversations.sort((a, b) => {{
                        // Closer to 1.0 ratio is more balanced
                        const balanceA = Math.abs(1 - (a.your_messages / a.their_messages || 1));
                        const balanceB = Math.abs(1 - (b.your_messages / b.their_messages || 1));
                        return balanceA - balanceB;
                    }});
                    break;
                case 'least_balanced':
                    filteredConversations.sort((a, b) => {{
                        // Further from 1.0 ratio is less balanced
                        const balanceA = Math.abs(1 - (a.your_messages / a.their_messages || 1));
                        const balanceB = Math.abs(1 - (b.your_messages / b.their_messages || 1));
                        return balanceB - balanceA;
                    }});
                    break;
                case 'closest':
                    filteredConversations.sort((a, b) => b.closeness_score - a.closeness_score);
                    break;
                case 'most_toxic':
                    filteredConversations.sort((a, b) => b.toxicity_score - a.toxicity_score);
                    break;
                case 'least_toxic':
                    filteredConversations.sort((a, b) => a.toxicity_score - b.toxicity_score);
                    break;
                case 'most_reliable':
                    filteredConversations.sort((a, b) => b.reliability_score - a.reliability_score);
                    break;
                case 'least_reliable':
                    filteredConversations.sort((a, b) => a.reliability_score - b.reliability_score);
                    break;
                case 'your_initiation':
                    filteredConversations.sort((a, b) => {{
                        const rateA = a.you_initiate / (a.you_initiate + a.they_initiate || 1);
                        const rateB = b.you_initiate / (b.you_initiate + b.they_initiate || 1);
                        return rateB - rateA;
                    }});
                    break;
                case 'their_initiation':
                    filteredConversations.sort((a, b) => {{
                        const rateA = a.they_initiate / (a.you_initiate + a.they_initiate || 1);
                        const rateB = b.they_initiate / (b.you_initiate + b.they_initiate || 1);
                        return rateB - rateA;
                    }});
                    break;
                case 'alphabetical':
                    filteredConversations.sort((a, b) => a.name.localeCompare(b.name));
                    break;
            }}

            if (updateAfter) {{
                updateDisplay();
            }}
        }}

        function searchNetwork() {{
            const searchTerm = document.getElementById('networkSearch').value.toLowerCase();
            const sortValue = document.getElementById('networkSortSelect').value;

            // Filter conversations based on search term
            let searchResults = filteredConversations.filter(conv =>
                conv.name.toLowerCase().includes(searchTerm)
            );

            // Apply current sort
            sortAndUpdateNetwork(sortValue, searchResults);
        }}

        function sortAndUpdateNetwork(sortBy, conversations = null) {{
            const sortLabels = {{
                'message_count': 'Message Count (Most to Least)',
                'recent': 'Most Recent Activity',
                'oldest': 'Oldest First',
                'duration': 'Longest Relationship',
                'balanced': 'Most Balanced',
                'least_balanced': 'Least Balanced',
                'closest': 'Closest Relationships',
                'most_toxic': 'Most Toxic',
                'least_toxic': 'Least Toxic',
                'most_reliable': 'Most Reliable',
                'least_reliable': 'Least Reliable',
                'your_initiation': 'You Initiate Most',
                'their_initiation': 'They Initiate Most',
                'alphabetical': 'Alphabetical'
            }};

            // Update network heading
            const searchTerm = document.getElementById('networkSearch').value;
            const headingText = searchTerm
                ? `🕸️ Relationship Network (search: "${{searchTerm}}", sorted by ${{sortLabels[sortBy] || sortBy}})`
                : `🕸️ Relationship Network (sorted by ${{sortLabels[sortBy] || sortBy}})`;
            document.getElementById('networkHeading').textContent = headingText;

            // Create a copy of filtered conversations and sort
            let networkConversations = conversations ? [...conversations] : [...filteredConversations];

            switch(sortBy) {{
                case 'message_count':
                    networkConversations.sort((a, b) => b.total_messages - a.total_messages);
                    break;
                case 'recent':
                    networkConversations.sort((a, b) => {{
                        const dateA = new Date(a.date_range.split(' to ')[1]);
                        const dateB = new Date(b.date_range.split(' to ')[1]);
                        return dateB - dateA;
                    }});
                    break;
                case 'oldest':
                    networkConversations.sort((a, b) => {{
                        const dateA = new Date(a.date_range.split(' to ')[0]);
                        const dateB = new Date(b.date_range.split(' to ')[0]);
                        return dateA - dateB;
                    }});
                    break;
                case 'duration':
                    networkConversations.sort((a, b) => {{
                        const durationA = new Date(a.date_range.split(' to ')[1]) - new Date(a.date_range.split(' to ')[0]);
                        const durationB = new Date(b.date_range.split(' to ')[1]) - new Date(b.date_range.split(' to ')[0]);
                        return durationB - durationA;
                    }});
                    break;
                case 'balanced':
                    networkConversations.sort((a, b) => {{
                        const balanceA = Math.abs(1 - (a.your_messages / a.their_messages || 1));
                        const balanceB = Math.abs(1 - (b.your_messages / b.their_messages || 1));
                        return balanceA - balanceB;
                    }});
                    break;
                case 'least_balanced':
                    networkConversations.sort((a, b) => {{
                        const balanceA = Math.abs(1 - (a.your_messages / a.their_messages || 1));
                        const balanceB = Math.abs(1 - (b.your_messages / b.their_messages || 1));
                        return balanceB - balanceA;
                    }});
                    break;
                case 'closest':
                    networkConversations.sort((a, b) => b.closeness_score - a.closeness_score);
                    break;
                case 'most_toxic':
                    networkConversations.sort((a, b) => b.toxicity_score - a.toxicity_score);
                    break;
                case 'least_toxic':
                    networkConversations.sort((a, b) => a.toxicity_score - b.toxicity_score);
                    break;
                case 'most_reliable':
                    networkConversations.sort((a, b) => b.reliability_score - a.reliability_score);
                    break;
                case 'least_reliable':
                    networkConversations.sort((a, b) => a.reliability_score - b.reliability_score);
                    break;
                case 'your_initiation':
                    networkConversations.sort((a, b) => {{
                        const rateA = a.you_initiate / (a.you_initiate + a.they_initiate || 1);
                        const rateB = b.you_initiate / (b.you_initiate + b.they_initiate || 1);
                        return rateB - rateA;
                    }});
                    break;
                case 'their_initiation':
                    networkConversations.sort((a, b) => {{
                        const rateA = a.they_initiate / (a.you_initiate + a.they_initiate || 1);
                        const rateB = b.they_initiate / (b.you_initiate + b.they_initiate || 1);
                        return rateB - rateA;
                    }});
                    break;
                case 'alphabetical':
                    networkConversations.sort((a, b) => a.name.localeCompare(b.name));
                    break;
            }}

            // Apply display limit to sorted network conversations
            const limitedNetworkConversations = networkConversations.slice(0, displayLimit);

            // Update network with sorted and limited conversations
            updateNetwork(limitedNetworkConversations);
        }}

        function updateDisplay() {{
            const displayed = filteredConversations.slice(0, displayLimit);
            displayedCount.textContent = displayed.length;

            // Show/hide filtered box
            if (currentFilter === 'all') {{
                filteredBox.style.display = 'none';
            }} else {{
                filteredBox.style.display = 'block';
                filteredCount.textContent = filteredConversations.length;
            }}

            // Update network
            updateNetwork(displayed);

            // Update conversation list
            updateConversationList(displayed);
        }}

        function updateNetwork(conversations) {{
            // Clear existing
            d3.select("#network").selectAll("*").remove();

            const width = document.getElementById('network').clientWidth;

            // Calculate dynamic height based on number of conversations being displayed
            const numConversations = conversations.length;
            // Start at 400px, add 4px per conversation up to max 1200px
            const height = Math.min(1200, Math.max(400, 400 + (numConversations * 4)));

            const nodes = [{{ id: "YOU", group: 0, size: 60 }}];
            const links = [];

            // All conversations passed in are already properly limited
            const maxMessages = Math.max(...conversations.map(c => c.total_messages));
            conversations.forEach((conv, i) => {{
                // Calculate node size based on message count (5-40 range)
                const nodeSize = 5 + (conv.total_messages / maxMessages) * 35;

                nodes.push({{
                    id: conv.name.length > 20 ? conv.name.substring(0, 17) + "..." : conv.name,
                    group: i + 1,
                    size: nodeSize,
                    filename: conv.filename,
                    messageCount: conv.total_messages
                }});

                // Calculate link distance: fewer messages = shorter line (50-300 range)
                const linkDistance = 50 + (conv.total_messages / maxMessages) * 250;

                links.push({{
                    source: "YOU",
                    target: nodes[nodes.length - 1].id,
                    value: conv.total_messages / 100,
                    distance: linkDistance
                }});
            }});

            const svg = d3.select("#network")
                .attr("width", width)
                .attr("height", height);

            const simulation = d3.forceSimulation(nodes)
                .force("link", d3.forceLink(links).id(d => d.id).distance(d => d.distance))
                .force("charge", d3.forceManyBody().strength(-200))
                .force("center", d3.forceCenter(width / 2, height / 2))
                .force("collision", d3.forceCollide().radius(d => d.size + 2));

            const link = svg.append("g")
                .selectAll("line")
                .data(links)
                .enter().append("line")
                .attr("stroke", "#999")
                .attr("stroke-opacity", 0.6)
                .attr("stroke-width", d => Math.sqrt(d.value));

            const tooltip = d3.select("#networkTooltip");

            const node = svg.append("g")
                .selectAll("g")
                .data(nodes)
                .enter().append("g")
                .attr("class", "node-group")
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended))
                .on("click", function(event, d) {{
                    if (d.filename) {{
                        window.location.href = d.filename + '_enhanced_dashboard.html';
                    }}
                }})
                .on("mouseover", function(event, d) {{
                    if (d.id !== "YOU") {{
                        const analysis = allAnalyses.find(a => a.filename === d.filename);
                        if (analysis) {{
                            let tooltipHTML = `<strong>${{d.id}}</strong>`;
                            tooltipHTML += `Messages: ${{d.messages.toLocaleString()}}<br>`;
                            tooltipHTML += `Type: ${{d.isGroup ? 'Group' : '1-on-1'}}<br>`;
                            if (analysis.date_range) {{
                                tooltipHTML += `Period: ${{analysis.date_range}}<br>`;
                            }}
                            if (analysis.their_analysis) {{
                                tooltipHTML += `Archetype: ${{analysis.their_analysis.archetypes.primary}}<br>`;
                                tooltipHTML += `MBTI: ${{analysis.their_analysis.mbti.type}}<br>`;
                            }}
                            tooltip.html(tooltipHTML)
                                .classed("visible", true)
                                .style("left", (event.pageX + 10) + "px")
                                .style("top", (event.pageY - 10) + "px");
                        }}
                    }}
                }})
                .on("mouseout", function() {{
                    tooltip.classed("visible", false);
                }})
                .on("mousemove", function(event) {{
                    tooltip.style("left", (event.pageX + 10) + "px")
                           .style("top", (event.pageY - 10) + "px");
                }});

            node.append("circle")
                .attr("r", d => d.size)
                .attr("fill", d => d.id === "YOU" ? "#667eea" : "#764ba2")
                .attr("stroke", "#fff")
                .attr("stroke-width", 2);

            // Add text background for better readability
            node.append("text")
                .text(d => d.id)
                .attr("x", 0)
                .attr("y", 5)
                .attr("text-anchor", "middle")
                .attr("fill", "rgba(0, 0, 0, 0.7)")
                .attr("font-size", d => d.id === "YOU" ? "14px" : "10px")
                .attr("font-weight", d => d.id === "YOU" ? "bold" : "normal")
                .attr("stroke", "rgba(0, 0, 0, 0.7)")
                .attr("stroke-width", 3)
                .attr("paint-order", "stroke");

            // Add white text on top
            node.append("text")
                .text(d => d.id)
                .attr("x", 0)
                .attr("y", 5)
                .attr("text-anchor", "middle")
                .attr("fill", "white")
                .attr("font-size", d => d.id === "YOU" ? "14px" : "10px")
                .attr("font-weight", d => d.id === "YOU" ? "bold" : "normal")
                .attr("pointer-events", "none");

            simulation.on("tick", () => {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);

                node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
            }});

            function dragstarted(event) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                event.subject.fx = event.subject.x;
                event.subject.fy = event.subject.y;
            }}

            function dragged(event) {{
                event.subject.fx = event.x;
                event.subject.fy = event.y;
            }}

            function dragended(event) {{
                if (!event.active) simulation.alphaTarget(0);
                event.subject.fx = null;
                event.subject.fy = null;
            }}
        }}

        function updateConversationList(conversations) {{
            const list = document.getElementById('conversationList');
            list.innerHTML = conversations.map((conv, i) => `
                <div class="conv-item" onclick="window.location.href='${{conv.filename}}_enhanced_dashboard.html'">
                    <div>
                        <div class="conv-name">#${{i+1}} ${{conv.name}}</div>
                        <div class="conv-stats">
                            ${{conv.total_messages.toLocaleString()}} messages |
                            ${{conv.date_range}} |
                            Your: ${{conv.your_archetype}} |
                            Them: ${{conv.their_archetype}}
                            ${{conv.is_group ? ' | GROUP' : ''}}
                        </div>
                    </div>
                    <div style="color: #667eea; font-size: 20px;">→</div>
                </div>
            `).join('');
        }}

        // Initial display
        updateDisplay();

        // Consistent archetype color mapping
        const archetypeColors = {{
            'Hero': '#3b82f6',      // Blue
            'Sage': '#8b5cf6',      // Purple
            'Innocent': '#ec4899',  // Pink
            'Jester': '#06b6d4',    // Cyan
            'Caregiver': '#10b981', // Green
            'Lover': '#f43f5e',     // Rose
            'Explorer': '#f59e0b',  // Amber
            'Creator': '#14b8a6',   // Teal
            'Ruler': '#6366f1',     // Indigo
            'Rebel': '#a855f7',     // Violet
            'Magician': '#0ea5e9',  // Sky
            'Everyperson': '#84cc16' // Lime
        }};

        // Get all unique archetypes from both datasets
        const yourData = {json.dumps(your_archetypes)};
        const theirData = {json.dumps(their_archetypes)};
        const allArchetypes = ['Hero', 'Sage', 'Innocent', 'Jester', 'Caregiver', 'Lover',
                               'Explorer', 'Creator', 'Ruler', 'Rebel', 'Magician', 'Everyperson'];

        // Create data arrays with 0 for missing values
        const yourValues = allArchetypes.map(arch => yourData[arch] || 0);
        const theirValues = allArchetypes.map(arch => theirData[arch] || 0);
        const colors = allArchetypes.map(arch => archetypeColors[arch]);

        // Combined archetype chart with nested donuts
        const archCtx = document.getElementById('archetypesChart').getContext('2d');
        new Chart(archCtx, {{
            type: 'doughnut',
            data: {{
                labels: allArchetypes,
                datasets: [
                    {{
                        label: 'You',
                        data: yourValues,
                        backgroundColor: colors,
                        borderWidth: 2,
                        borderColor: '#fff'
                    }},
                    {{
                        label: 'Them',
                        data: theirValues,
                        backgroundColor: colors.map(c => c + '80'), // Add transparency
                        borderWidth: 2,
                        borderColor: '#fff'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            boxWidth: 15,
                            font: {{
                                size: 12
                            }},
                            padding: 10,
                            generateLabels: function(chart) {{
                                const datasets = chart.data.datasets;
                                const archetypes = chart.data.labels;

                                // Create archetype labels
                                const archetypeLabels = archetypes.map((label, i) => ({{
                                    text: label,
                                    fillStyle: colors[i],
                                    hidden: false,
                                    index: i
                                }}));

                                // Add dataset labels (You/Them)
                                const datasetLabels = [
                                    {{ text: '■ You (inner)', fillStyle: '#667eea', hidden: false }},
                                    {{ text: '□ Them (outer)', fillStyle: '#667eea80', hidden: false }}
                                ];

                                return [...datasetLabels, ...archetypeLabels];
                            }}
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const label = context.dataset.label || '';
                                const value = context.parsed || 0;
                                return label + ': ' + value.toFixed(1) + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""

    master_path = CONVERSATIONS_DIR / "00_INTERACTIVE_MASTER.html"
    with open(master_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return master_path

if __name__ == "__main__":
    html_path = create_interactive_master()
    print(f"✓ Interactive master dashboard created: {html_path}")
    print(f"✓ Features:")
    print(f"  - Adjustable slider (5 to all conversations)")
    print(f"  - Preset buttons (Top 5, 10, 50, 200, 400, All)")
    print(f"  - Filter by type (All, 1-on-1, Groups)")
    print(f"  - Clickable network nodes and conversation items")

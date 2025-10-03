# MessageAnalyzer

> Comprehensive text message conversation analysis using psychological profiling, relationship dynamics, and interactive visualizations

**Version:** 1.0
**Last Updated:** October 2, 2025
**Status:** Active Development

---

## 📋 Project Overview

MessageAnalyzer extracts text message conversations from macOS Messages database backups and performs comprehensive psychological analysis including personality profiling (Jungian archetypes, Enneagram, MBTI, attachment styles), emotion detection, and relationship dynamics scoring. Results are presented through interactive HTML dashboards with network visualizations, timelines, and searchable message viewers.

### What This Does

1. **Extracts** all conversations from Messages database (iMessage/SMS)
2. **Analyzes** conversations using psychological frameworks & keyword analysis
3. **Visualizes** results through interactive HTML dashboards
4. **Scores** relationships on closeness, toxicity, and reliability metrics
5. **Provides** searchable message history with export capabilities

---

## 🚀 Quick Start

### Prerequisites
- macOS with Messages app
- Python 3.x
- Messages database backup at `data/raw/chat_copy.db`

### Run Complete Analysis (5 steps)

```bash
cd ~/Documents/Python/Projects/MessageAnalyzer

# 1. Extract conversations
python3 src/extract_conversations.py

# 2. Analyze all conversations
python3 src/analyze_conversations.py

# 3. Generate individual dashboards
python3 src/generate_individual_dashboards.py

# 4. Categorize relationships
python3 src/categorize_relationships.py

# 5. Create master dashboard
python3 src/generate_master_dashboard.py

# Open master dashboard
open data/output/all_conversations/00_INTERACTIVE_MASTER.html
```

---

## 📁 Project Structure

```
MessageAnalyzer/
├── README.md                     # ← START HERE (this file)
├── PROJECT_STRUCTURE.md          # Detailed architecture reference
├── TODO.md                       # Task tracking & roadmap
│
├── src/                          # Source code
│   ├── extract_conversations.py           # Step 1: Extract from DB
│   ├── analyze_conversations.py           # Step 2: Analyze all
│   ├── generate_individual_dashboards.py  # Step 3: Create dashboards
│   ├── categorize_relationships.py        # Step 4: Score relationships
│   ├── generate_master_dashboard.py       # Step 5: Master overview
│   ├── add_contact_names.py               # Utility: Map numbers to names
│   ├── analyze_conversation.py            # Library: Core analysis
│   ├── analyze_with_evidence.py           # Library: Evidence-based analysis
│   └── create_message_viewer_dashboard.py # Library: Dashboard generator
│
├── data/                         # Data files (gitignored)
│   ├── raw/                      # Original data
│   │   └── chat_copy.db          # Messages database backup
│   └── output/                   # Generated files
│       └── all_conversations/    # Analysis results & dashboards
│
├── docs/                         # Documentation
│   ├── algorithms/               # How analysis works
│   │   └── methodology_documentation.md
│   ├── design/                   # Architecture & decisions
│   │   └── CODE_AUDIT.md
│   └── guides/                   # How-to guides
│       └── README_MESSAGES_EXPORT.md
│
├── config/                       # Configuration
│   └── paths.py                  # Centralized paths
│
└── tests/                        # Tests (future)
```

---

## 🧠 Analysis Capabilities

### Psychological Profiling
- **Jungian Archetypes** (12 types): Hero, Sage, Explorer, Innocent, Caregiver, Rebel, Magician, Lover, Jester, Everyperson, Ruler, Creator
- **Enneagram** (9 types): Perfectionist, Helper, Achiever, Individualist, Investigator, Loyalist, Enthusiast, Challenger, Peacemaker
- **MBTI** (16 types): I/E, N/S, T/F, J/P dimensions
- **Attachment Styles** (4 types): Secure, Anxious, Avoidant, Disorganized

### Emotion Analysis
- Joy, Sadness, Anger, Fear, Love, Gratitude
- Temporal emotion tracking (sentiment timeline)

### Relationship Dynamics
- **Message Balance**: Who sends more messages
- **Initiation Patterns**: Who starts conversations
- **Responsiveness**: Quick response rates
- **Closeness Score** (0-100): Overall relationship health
- **Toxicity Score** (0-100): Negative patterns indicator
- **Reliability Score** (0-100): Dependability measure

### Communication Patterns
- Average/median message length
- Question frequency
- Emoji usage
- Exclamation usage

---

## 📊 Dashboard Features

### Master Dashboard
- Interactive D3.js network graph (YOU at center)
- 14 sorting options (message count, recent, balance, toxicity, etc.)
- Searchable network
- Filter by 1-on-1 vs group conversations
- Adjustable display limits (5 to all conversations)

### Individual Dashboards
- Full conversation message viewer (searchable)
- Export to JSON/TXT
- Psychological profile radar charts
- Timeline charts (message activity & emotional arc)
- Evidence citations for personality claims
- Tabbed interface (Overview, Messages, Timeline)

---

## 🔄 Current Status

### ✅ Completed (Last Session: Oct 2, 2025)

**Code Cleanup:**
- Deleted 7 deprecated files (44% codebase reduction)
- Renamed 4 files with clearer names
- Fixed broken import dependencies
- Eliminated ~3,000 lines of redundant code

**Project Organization:**
- Moved to proper directory structure
- Organized files by type (src, data, docs)
- Created PROJECT_STRUCTURE.md
- Created centralized config/paths.py

**Dashboard Features:**
- Message viewer with search & export
- Network graph with 14 sort options
- Fixed navigation (no new tabs, back button)
- Dynamic height calculation
- Proper display limit enforcement

### 🚧 In Progress / Next Steps

See **TODO.md** for complete list. High priority items:

1. **Update Python scripts** to use new path structure (config/paths.py)
2. **Test scripts** work with new directory layout
3. **Add radar charts** for top 7 archetypes to individual dashboards
4. **Fix Messages tab** visibility issue (if still present)
5. **Research LLMs** for improved analysis (Llama, Mistral)
6. **Enhance UI interactivity** (hover tooltips, drill-downs)

---

## 📚 Key Documentation Files

| File | Purpose | When to Read |
|------|---------|--------------|
| **README.md** | Project overview & quick start | **READ THIS FIRST** |
| **PROJECT_STRUCTURE.md** | Detailed architecture & file locations | When you need to find something |
| **TODO.md** | Task tracking & roadmap | To see what needs doing |
| **CODE_AUDIT.md** | Code cleanup report & decisions | To understand recent changes |
| **methodology_documentation.md** | How analysis algorithms work | To understand the psychology |

---

## ⚙️ Technical Details

### Analysis Methodology
- **Keyword-based matching**: Simple but fast
- **No ML/AI currently**: Uses predefined keyword lists
- **Limitations**: Cannot detect sarcasm, context, or cultural nuance
- See `docs/algorithms/methodology_documentation.md` for details

### Technology Stack
- **Backend**: Python 3 (stdlib only, no external deps currently)
- **Database**: SQLite3 (Messages database)
- **Frontend**: HTML/CSS/JavaScript
- **Visualization**: Chart.js, D3.js (loaded via CDN)

### Scoring Algorithms
- **Closeness Score**: Message balance (20) + responsiveness (15) + secure attachment (30) + positive emotions (20) + volume (15)
- **Toxicity Score**: Negative emotions (50) + insecure attachment (30) + imbalance (10) + response imbalance (10)
- **Reliability Score**: Their responsiveness (30) + secure attachment (25) + supportive archetype (20) + balance (15) + reliable enneagram (10)

---

## 🔬 Known Limitations

### Analysis Accuracy
- Keyword-based (not true NLP/sentiment analysis)
- English-optimized only
- No emoji/multimedia analysis
- Cannot detect sarcasm or context
- Cultural biases in keyword selection
- **Future**: Research LLM-based approaches (see TODO.md)

### Technical Debt
- No error handling for missing files
- Division by zero in small conversations
- No logging framework
- No unit tests yet
- Hard-coded paths (being migrated to config)

---

## 🤝 For AI Assistants / Future Sessions

### Context Recovery Protocol

When starting a new session:

1. **Read this README.md first** - Get project overview
2. **Read TODO.md** - Understand current priorities
3. **Read PROJECT_STRUCTURE.md** - Find file locations
4. **Check latest in docs/design/** - Recent architectural changes

### Common Tasks

**To understand the analysis:**
→ Read `docs/algorithms/methodology_documentation.md`

**To find a specific file/function:**
→ Check `PROJECT_STRUCTURE.md` (has dependency graph)

**To continue development:**
→ Check `TODO.md` for prioritized tasks

**To understand recent changes:**
→ Read `docs/design/CODE_AUDIT.md`

### Session Handoff Notes

**Last worked on (Oct 2, 2025):**
- Completed project reorganization
- All files moved to proper structure
- Created comprehensive documentation
- **Next step**: Update Python scripts to use config/paths.py

**Current blockers:** None

**Testing needed:**
- Scripts must be updated for new paths before testing
- Master dashboard sorting with display limits (recently fixed)

---

## 📝 Development Workflow

### Adding a New Feature

1. Update `TODO.md` with task
2. Implement in appropriate `src/` file
3. Update `PROJECT_STRUCTURE.md` if architecture changes
4. Test manually (no test suite yet)
5. Update this README if it's a major feature
6. Mark task complete in `TODO.md`

### Debugging

- Check console output (scripts print progress)
- Verify data files exist in expected locations
- Check browser console for dashboard errors
- See `docs/design/CODE_AUDIT.md` for known issues

---

## 🎯 Project Goals

### Short-term
- ✅ Extract and analyze text messages
- ✅ Create interactive dashboards
- ✅ Organize codebase properly
- 🔲 Add comprehensive testing
- 🔲 Improve analysis accuracy

### Medium-term
- Research LLM-based analysis (local deployment)
- Add academic-level statistical measures
- Enhance UI interactivity (tooltips, drill-downs)
- Implement virtual environment & dependency management

### Long-term
- Multi-language support
- Real-time analysis integration
- Comparison views (multiple relationships)
- Export to academic formats (CSV, LaTeX)

---

## 🐛 Troubleshooting

### "No such file or directory" errors
→ Ensure you're running scripts from project root
→ Check database exists at `data/raw/chat_copy.db`

### Dashboards won't open
→ Check browser console for errors
→ Verify HTML files in `data/output/all_conversations/`

### Analysis results seem wrong
→ See `docs/algorithms/methodology_documentation.md` for limitations
→ Keyword-based analysis has known accuracy issues

### Import errors
→ All scripts should be run from project root
→ Python files import from same `src/` directory

---

## 📄 License & Privacy

- **Code**: No license yet (personal project)
- **Data**: All analysis runs locally, no data sent to external servers
- **Privacy**: User is responsible for securing their Messages database backup

---

## 🔗 Quick Links

- **Start analyzing**: Run the 5-step workflow above
- **Understand analysis**: `docs/algorithms/methodology_documentation.md`
- **Find files**: `PROJECT_STRUCTURE.md`
- **See tasks**: `TODO.md`
- **Recent changes**: `docs/design/CODE_AUDIT.md`

---

**For questions or issues, consult the documentation files above or update TODO.md with new tasks.**

**Last session ended:** Completed project reorganization, created comprehensive docs
**Next session should:** Update scripts to use config/paths.py, then test workflow

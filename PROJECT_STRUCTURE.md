# MessageAnalyzer Project Structure

**Last Updated:** October 2, 2025

---

## Directory Structure

```
MessageAnalyzer/
├── src/                          # Source code
│   ├── extract_conversations.py           # Extract conversations from Messages DB
│   ├── analyze_conversations.py           # Analyze all conversations
│   ├── analyze_conversation.py            # Core analysis engine (library)
│   ├── analyze_with_evidence.py           # Analysis with evidence citations (library)
│   ├── generate_individual_dashboards.py  # Create individual dashboards
│   ├── generate_master_dashboard.py       # Create master overview dashboard
│   ├── create_message_viewer_dashboard.py # Dashboard generator (library)
│   ├── categorize_relationships.py        # Categorize by closeness/toxicity/reliability
│   └── add_contact_names.py               # Map phone numbers to names
│
├── data/                         # Data files
│   ├── raw/                      # Original/raw data
│   │   ├── chat_copy.db          # Messages database backup
│   │   └── *_messages.json       # Individual conversation exports
│   ├── processed/                # Intermediate processing files
│   └── output/                   # Generated output
│       └── all_conversations/    # All extracted conversations & dashboards
│
├── docs/                         # Documentation
│   ├── algorithms/               # Algorithm explanations
│   │   └── methodology_documentation.md
│   ├── design/                   # Design decisions & architecture
│   │   └── CODE_AUDIT.md
│   ├── guides/                   # User guides & how-tos
│   │   └── README_MESSAGES_EXPORT.md
│   └── summaries/                # Project summaries
│
├── tests/                        # Unit tests (future)
├── config/                       # Configuration files
│   └── paths.py                  # Centralized path configuration
└── TODO.md                       # Project tasks

```

---

## File Locations Quick Reference

### Scripts (Entry Points)

| Script | Location | Purpose |
|--------|----------|---------|
| **extract_conversations.py** | `src/` | Extract all conversations from Messages database |
| **analyze_conversations.py** | `src/` | Batch analyze all conversations |
| **generate_individual_dashboards.py** | `src/` | Create HTML dashboards for each conversation |
| **categorize_relationships.py** | `src/` | Score relationships (closeness/toxicity/reliability) |
| **generate_master_dashboard.py** | `src/` | Create master overview with network graph |
| **add_contact_names.py** | `src/` | Utility to map phone numbers to readable names |

### Library Modules (Imported by Scripts)

| Module | Location | Purpose |
|--------|----------|---------|
| **analyze_conversation.py** | `src/` | Core psychological analysis engine |
| **analyze_with_evidence.py** | `src/` | Analysis with evidence citations |
| **create_message_viewer_dashboard.py** | `src/` | Individual dashboard HTML generator |

### Configuration

| File | Location | Purpose |
|------|----------|---------|
| **paths.py** | `config/` | Centralized path configuration for all scripts |

### Data Files

| Type | Location | Description |
|------|----------|-------------|
| **Database** | `data/raw/chat_copy.db` | Messages database backup |
| **Raw exports** | `data/raw/*_messages.json` | Individual conversation JSON files |
| **Processed data** | `data/output/all_conversations/` | Extracted conversations, analysis, dashboards |

### Documentation

| Document | Location | Content |
|----------|----------|---------|
| **methodology_documentation.md** | `docs/algorithms/` | Detailed explanation of analysis methodology |
| **CODE_AUDIT.md** | `docs/design/` | Code cleanup report & architecture decisions |
| **README_MESSAGES_EXPORT.md** | `docs/guides/` | How to export messages from macOS |
| **PROJECT_STRUCTURE.md** | Root | This file - project organization reference |
| **TODO.md** | Root | Task tracking |

---

## Workflow & Execution Order

### Standard Workflow

1. **Extract conversations from database**
   ```bash
   python3 src/extract_conversations.py
   ```
   - Reads: `data/raw/chat_copy.db`
   - Outputs: `data/output/all_conversations/*.json`

2. **Analyze all conversations**
   ```bash
   python3 src/analyze_conversations.py
   ```
   - Reads: `data/output/all_conversations/*.json`
   - Outputs: `data/output/all_conversations/*_analysis.json`

3. **Generate individual dashboards**
   ```bash
   python3 src/generate_individual_dashboards.py
   ```
   - Reads: `data/output/all_conversations/*.json`
   - Outputs: `data/output/all_conversations/*_enhanced_dashboard.html`

4. **Categorize relationships**
   ```bash
   python3 src/categorize_relationships.py
   ```
   - Reads: `data/output/all_conversations/*_analysis.json`
   - Outputs: `data/output/all_conversations/00_RELATIONSHIP_CATEGORIES.json`

5. **Generate master dashboard**
   ```bash
   python3 src/generate_master_dashboard.py
   ```
   - Reads: All analysis and category files
   - Outputs: `data/output/all_conversations/00_INTERACTIVE_MASTER.html`

### Optional Utilities

**Add contact names:**
```bash
python3 src/add_contact_names.py
```

---

## Import Dependencies

### Dependency Graph

```
extract_conversations.py (standalone)
    └── No project dependencies

analyze_conversation.py (library)
    └── No project dependencies

analyze_with_evidence.py (library)
    └── imports: analyze_conversation

analyze_conversations.py (script)
    └── imports: analyze_conversation

create_message_viewer_dashboard.py (library)
    └── imports: analyze_with_evidence

generate_individual_dashboards.py (script)
    └── imports: create_message_viewer_dashboard

generate_master_dashboard.py (standalone)
    └── No project dependencies

categorize_relationships.py (standalone)
    └── No project dependencies

add_contact_names.py (utility)
    └── imports: create_message_viewer_dashboard
```

**No circular dependencies** ✓

---

## Code Standards & Conventions

### Naming Conventions
- **Scripts**: `verb_noun.py` (e.g., `extract_conversations.py`, `analyze_conversations.py`)
- **Libraries**: `verb_noun.py` (e.g., `analyze_conversation.py`)
- **Functions**: `snake_case` (e.g., `analyze_conversation()`)
- **Classes**: `PascalCase` (if used)

### Import Standards
- All imports use relative imports within flat `src/` directory
- Standard library imports first, then project imports
- Use `from module import function` for frequently used functions

### File Organization
- Entry point scripts in `src/` root
- Library modules (imported by others) also in `src/`
- All data separated into `data/` subdirectories
- Documentation organized by type in `docs/`

---

## Design Decisions

### Why This Structure?

1. **Flat `src/` directory**: All Python files in one place since project is small
2. **Separate `data/` hierarchy**: Clear separation of raw vs processed vs output
3. **Organized `docs/`**: Documentation by type (algorithms, design, guides)
4. **Centralized `config/`**: Single source of truth for paths

### Key Architectural Choices

- **Library modules**: Core analysis logic in reusable modules
- **Entry point scripts**: Workflow orchestration separate from logic
- **No classes**: Simple functional approach (may refactor later)
- **HTML generation**: Embedded in Python (could extract to templates later)

---

## Features & Capabilities

### Analysis Features
- Jungian Archetype Detection (12 archetypes)
- Enneagram Type Analysis (9 types)
- MBTI Personality Type (16 types)
- Attachment Style Analysis (4 styles)
- Emotion Detection (6 core emotions)
- Relationship Dynamics (initiation, responsiveness, balance)

### Dashboard Features
- Interactive network graph (D3.js)
- Searchable message viewer
- Timeline charts (activity & sentiment)
- Radar charts for psychological profiles
- Export functionality (JSON & TXT)
- Sorting & filtering (14 sort options)

### Scoring Metrics
- Closeness Score (0-100)
- Toxicity Score (0-100)
- Reliability Score (0-100)

---

## Testing Status

### Currently Tested
- Manual testing of all workflows
- Visual inspection of dashboards
- Data validation for extracted conversations

### Not Yet Tested (See TODO.md)
- Unit tests for analysis functions
- Edge case handling
- Large dataset performance (>1000 conversations)

---

## External Dependencies

### Required Python Libraries
- `sqlite3` - Database access
- `json` - Data handling
- `datetime` - Timestamp processing
- `collections.Counter` - Keyword frequency
- `pathlib` - Path handling
- `glob` - File pattern matching
- `re` - Regular expressions

### Frontend Libraries (CDN)
- Chart.js - Data visualization
- D3.js - Network graphs

### No Virtual Environment Yet
- **TODO**: Create requirements.txt
- **TODO**: Set up virtual environment with dependency checking

---

## Known Issues & Limitations

### Analysis Limitations
- Keyword-based (doesn't understand context/sarcasm)
- English-optimized only
- Limited emoji analysis
- No multimedia message analysis

### Technical Debt
- Hard-coded paths (being migrated to `config/paths.py`)
- No error handling for missing files
- Division by zero in small conversations
- No logging framework

See `CODE_AUDIT.md` and `TODO.md` for complete list.

---

## Future Enhancements

### High Priority
- Radar charts for top 7 archetypes
- Collapsible methodology sections
- Enhanced UI interactivity (hover tooltips, drill-downs)

### Research Areas
- LLM-based analysis (Llama, Mistral)
- Academic methodology review
- Professional psycholinguistic features

See `TODO.md` for complete roadmap.

---

## Quick Start Guide

### First Time Setup
1. Place Messages database at `data/raw/chat_copy.db`
2. Run extraction: `python3 src/extract_conversations.py`
3. Run analysis: `python3 src/analyze_conversations.py`
4. Generate dashboards: `python3 src/generate_individual_dashboards.py`
5. Open master dashboard: `open data/output/all_conversations/00_INTERACTIVE_MASTER.html`

### Adding Names
1. Run: `python3 src/add_contact_names.py`
2. Follow interactive prompts to map phone numbers to names

---

## Support & Contact

- **Issues**: See `TODO.md` for known tasks
- **Architecture**: See `docs/design/CODE_AUDIT.md`
- **Methodology**: See `docs/algorithms/methodology_documentation.md`

---

**End of Structure Documentation**

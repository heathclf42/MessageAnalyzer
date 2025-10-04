# File Placement Rules
**Last Updated:** 2025-10-03

## Purpose
This document defines **where every type of file belongs** to prevent future organizational chaos.

---

## Quick Reference

| File Type | Location | Example |
|-----------|----------|---------|
| **User-facing scripts** | `scripts/` | `scripts/run_analysis.py` |
| **Core library code** | `src/` | `src/stage2/weekly_analyzer.py` |
| **Tests** | `tests/` | `tests/unit/test_validators.py` |
| **Developer tools** | `tools/` | `tools/preview/preview_chunks.py` |
| **Documentation** | `docs/` | `docs/guides/quick_start.md` |
| **Configuration** | `config/` | `config/paths.py` |
| **Data outputs** | `data/output/` | `data/output/dashboards/` |

---

## Detailed Rules

### 1. ROOT DIRECTORY (`/`)
**Allowed:**
- `README.md` - Project overview
- `TODO.md` - Project todo list
- `.gitignore` - Git ignore rules
- `requirements.txt` - Python dependencies
- `.claude_project` - Claude Code config
- `LICENSE` - Project license
- `setup.py` / `pyproject.toml` - Package config (if needed)

**NOT Allowed:**
- ❌ Python scripts (`.py` files)
- ❌ Additional markdown files
- ❌ Test files
- ❌ Data files

**Rule:** Root should only contain project metadata and configuration

---

### 2. SCRIPTS DIRECTORY (`scripts/`)
**Purpose:** User-facing CLI entry points

**Allowed:**
- Main analysis runners
- Dashboard generators
- Data extraction tools

**Examples:**
```
scripts/
├── run_analysis.py          # Main CLI entry point
├── generate_dashboard.py    # Dashboard generation
├── extract_data.py           # Data extraction
└── README.md                 # How to use scripts
```

**Naming Convention:**
- Use verb_noun format: `run_analysis.py`, `generate_dashboard.py`
- Keep names short and descriptive
- No version numbers or dates in filenames

**NOT Allowed:**
- ❌ Library code with reusable functions (belongs in `src/`)
- ❌ Test files (belongs in `tests/`)
- ❌ Experimental/preview tools (belongs in `tools/`)

---

### 3. SOURCE DIRECTORY (`src/`)
**Purpose:** Core library code, organized by functionality

**Structure:**
```
src/
├── core/                     # Shared utilities
│   ├── __init__.py
│   ├── llm_client.py
│   ├── validators.py
│   └── parsers.py
├── stage1/                   # Stage 1: Single analysis
│   ├── __init__.py
│   ├── analyzer.py
│   └── evidence_parser.py
├── stage2/                   # Stage 2: Weekly analysis
│   ├── __init__.py
│   ├── weekly_analyzer.py
│   └── citation_analyzer.py
├── dashboard/                # Dashboard generation
│   ├── __init__.py
│   ├── builder.py
│   ├── templates/
│   └── components/
└── extractors/               # Data extraction
    ├── __init__.py
    ├── conversation_extractor.py
    └── contact_manager.py
```

**Rules:**
- All directories must have `__init__.py`
- Group by feature/stage, not by file type
- Use clear, descriptive module names
- No "utils" dumping ground - be specific

**NOT Allowed:**
- ❌ CLI scripts (belongs in `scripts/`)
- ❌ Test files (belongs in `tests/`)
- ❌ Standalone tools (belongs in `tools/`)

---

### 4. TESTS DIRECTORY (`tests/`)
**Purpose:** All test code

**Structure:**
```
tests/
├── unit/                     # Unit tests
│   ├── test_validators.py
│   ├── test_parsers.py
│   └── test_extractors.py
├── integration/              # Integration tests
│   ├── test_stage1_pipeline.py
│   ├── test_stage2_pipeline.py
│   └── test_dashboard_gen.py
├── experimental/             # Exploratory/prototype tests
│   ├── test_bert_range.py
│   └── test_llm_models.py
├── fixtures/                 # Test data
│   ├── sample_conversations.json
│   └── expected_outputs/
└── conftest.py               # Pytest configuration
```

**Naming Convention:**
- Prefix all test files with `test_`
- Mirror src structure: `src/core/validators.py` → `tests/unit/test_validators.py`

**NOT Allowed:**
- ❌ Non-test Python files
- ❌ Production code

---

### 5. TOOLS DIRECTORY (`tools/`)
**Purpose:** Developer/debugging tools (not for end users)

**Structure:**
```
tools/
├── preview/                  # Data preview tools
│   ├── preview_chunks.py
│   ├── preview_prompts.py
│   └── preview_outputs.py
├── compare/                  # Comparison tools
│   ├── compare_citations.py
│   └── compare_models.py
└── debug/                    # Debugging utilities
    ├── inspect_json.py
    └── validate_structure.py
```

**Rules:**
- Tools are for development/debugging only
- Not imported by production code
- Can be messy/experimental
- Include README explaining each tool

---

### 6. DOCUMENTATION DIRECTORY (`docs/`)
**Purpose:** All markdown documentation

**Structure:**
```
docs/
├── INDEX.md                  # Central documentation index
├── architecture/             # System design
│   ├── overview.md
│   ├── stage1.md
│   ├── stage2.md
│   └── ensemble_model.md
├── algorithms/               # Technical methodology
│   ├── methodology.md
│   ├── validation.md
│   └── prompt_refinement.md
├── guides/                   # User guides
│   ├── getting_started.md
│   ├── exporting_messages.md
│   ├── running_analysis.md
│   └── interpreting_results.md
├── reference/                # API & configuration
│   ├── file_locations.md
│   ├── models.md
│   ├── prompts.md
│   └── api/
├── development/              # Developer docs
│   ├── code_standards.md
│   ├── testing.md
│   ├── contributing.md
│   └── FILE_PLACEMENT_RULES.md (this file)
└── decisions/                # Architecture Decision Records
    ├── 001_llm_selection.md
    └── 002_weekly_windowing.md
```

**Categories:**
- **architecture/** - System design documents
- **algorithms/** - Technical methodologies
- **guides/** - Step-by-step instructions for users
- **reference/** - API docs, configurations, lookups
- **development/** - For contributors/developers
- **decisions/** - ADRs (why we made certain choices)

**Naming Convention:**
- Use snake_case: `getting_started.md`
- Be descriptive: `exporting_messages.md` not `export.md`
- ADRs numbered: `001_topic.md`

---

### 7. CONFIGURATION DIRECTORY (`config/`)
**Purpose:** Configuration files and settings

**Structure:**
```
config/
├── __init__.py
├── paths.py                  # Path constants
├── models.json               # Model configurations
├── prompts/                  # Prompt templates
│   ├── stage1_template.txt
│   └── stage2_template.txt
└── credentials.example.json  # Template (not real credentials!)
```

**Rules:**
- No credentials/secrets committed (use .example files)
- All paths defined in one place (`paths.py`)
- Configuration is data, not code

---

### 8. DATA DIRECTORY (`data/`)
**Purpose:** All data files (input and output)

**Structure:**
```
data/
├── raw/                      # Original message exports
│   └── {export_date}/
├── processed/                # Extracted conversations
│   └── conversations/
├── output/
│   ├── analysis/             # Analysis results
│   │   ├── stage1/
│   │   └── stage2/
│   ├── dashboards/           # HTML outputs
│   ├── images/               # Generated charts
│   └── monitoring/           # LLM metrics
└── .gitignore                # Ignore all data/output/
```

**Rules:**
- Data files NEVER committed to git
- Organize by date/phone number
- Implement cleanup policy (archive old files)

---

## Decision Flowchart

```
┌─────────────────────────────────────┐
│ Where does this file belong?        │
└──────────┬──────────────────────────┘
           │
           ├─ Is it a CLI for users? ──────────────> scripts/
           │
           ├─ Is it reusable library code? ────────> src/{module}/
           │
           ├─ Is it a test? ───────────────────────> tests/{type}/
           │
           ├─ Is it a dev/debug tool? ─────────────> tools/{category}/
           │
           ├─ Is it documentation? ────────────────> docs/{category}/
           │
           ├─ Is it configuration? ────────────────> config/
           │
           ├─ Is it data/output? ──────────────────> data/{type}/
           │
           └─ Is it project metadata? ─────────────> / (root)
```

---

## Enforcement

### Pre-commit Checks
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Check for Python files in root
root_py=$(git diff --cached --name-only --diff-filter=A | grep "^[^/]*\.py$")
if [ -n "$root_py" ]; then
    echo "❌ Error: Python files not allowed in root directory"
    echo "   Move to scripts/ or src/"
    echo "   Files: $root_py"
    exit 1
fi

# Check for MD files in root (except allowed)
allowed_md="README.md TODO.md LICENSE.md"
root_md=$(git diff --cached --name-only --diff-filter=A | grep "^[^/]*\.md$")
for file in $root_md; do
    if ! echo "$allowed_md" | grep -q "$file"; then
        echo "❌ Error: Markdown file not allowed in root: $file"
        echo "   Move to docs/{ architecture | guides | reference | development}"
        exit 1
    fi
done
```

### GitHub Actions (Optional)
```yaml
# .github/workflows/structure-check.yml
name: File Structure Check
on: [pull_request]
jobs:
  check-structure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check root directory
        run: |
          if ls *.py 2>/dev/null; then
            echo "Python files found in root!"
            exit 1
          fi
```

---

## Quick Commands

### Check for misplaced files
```bash
# Python files in root
ls *.py 2>/dev/null && echo "❌ Move to scripts/ or src/"

# Extra MD files in root
ls *.md | grep -v "README.md\|TODO.md\|LICENSE.md" && echo "❌ Move to docs/"

# Test files outside tests/
find src/ -name "test_*.py" && echo "❌ Move to tests/"
```

### Auto-organize (run carefully!)
```bash
# Move test files
find . -maxdepth 1 -name "test_*.py" -exec mv {} tests/experimental/ \;

# Move preview tools
find . -maxdepth 1 -name "preview_*.py" -o -name "compare_*.py" -exec mv {} tools/preview/ \;

# Move runner scripts
find . -maxdepth 1 -name "run_*.py" -o -name "analyze_*.py" -exec mv {} scripts/ \;
```

---

## When in Doubt

**Ask these questions:**

1. **Will a user run this directly?** → `scripts/`
2. **Will it be imported by other code?** → `src/`
3. **Is it testing something?** → `tests/`
4. **Is it explaining something?** → `docs/`
5. **Is it a one-off debug tool?** → `tools/`

**Still unsure?** Ask in team chat or create a GitHub discussion.

---

## Exceptions

**Rare cases where rules can be broken:**
- Temporary analysis scripts during exploration (delete when done)
- One-time migration scripts (move to `tools/migration/` after use)
- Emergency hotfixes (clean up later)

**Document exceptions** in commit messages and TODO.md

---

**This is a living document.** Update as the project evolves!

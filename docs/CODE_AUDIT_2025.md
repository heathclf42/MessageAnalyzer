# Code Audit & Refactoring Recommendations
**Date:** 2025-10-03
**Project:** MessageAnalyzer

## Executive Summary
This audit identifies structural issues, redundancies, and recommendations for improving code quality, maintainability, and documentation.

---

## 1. REDUNDANT & SIMILARLY NAMED FILES

### 1.1 Analysis Scripts (Potential Redundancy)
- **`analyze_single_conversation.py`** (root)
- **`src/analyze_conversation.py`**
- **`src/analyze_conversations.py`**
- **`src/analyze_with_evidence.py`**

**Issue:** Multiple analysis scripts with overlapping functionality
**Recommendation:** Consolidate into single entry point with CLI flags:
```bash
python src/analyze.py --mode=single --phone=XXX
python src/analyze.py --mode=batch --all
python src/analyze.py --mode=evidence --phone=XXX
```

### 1.2 LLM Analysis Files
- **`add_llm_analysis.py`** (root)
- **`src/llm_analyzer.py`**
- **`src/stage2_llm_analyzer.py`**

**Issue:** Unclear separation between stages
**Recommendation:**
- Keep `src/stage1_llm_analyzer.py` (rename from llm_analyzer.py)
- Keep `src/stage2_llm_analyzer.py`
- Delete `add_llm_analysis.py` or make it a CLI wrapper

### 1.3 Dashboard Creation Scripts
- **`src/create_llm_dashboard.py`**
- **`src/create_message_viewer_dashboard.py`**
- **`src/create_weekly_dashboard.py`**
- **`src/add_citation_to_dashboard.py`**
- **`src/add_weekly_metrics_to_dashboard.py`**
- **`src/optimize_dashboard_ui.py`**

**Issue:** Too many dashboard scripts
**Recommendation:** Create unified dashboard builder:
```python
src/dashboard_builder.py
  ├── build_base_dashboard()
  ├── add_stage1_analysis()
  ├── add_stage2_weekly()
  ├── add_citations()
  └── optimize_ui()
```

### 1.4 Test Files (Root Directory)
All test files are in root - should be in `tests/` directory:
- `test_bert_range.py`
- `test_embedded_prompts.py`
- `test_llm_models.py`
- `test_model_outputs.py`
- `test_models.py`
- `test_speaker_separation.py`

**Recommendation:** Move to `tests/` with structured naming:
```
tests/
  ├── unit/
  ├── integration/
  └── experimental/
      ├── test_bert_range.py
      ├── test_llm_models.py
      └── test_speaker_separation.py
```

### 1.5 Preview/Debug Scripts (Root Directory)
- `preview_chunks.py`
- `preview_stage1_inputs.py`
- `preview_test_prompts.py`

**Recommendation:** Move to `tools/debug/` or `scripts/preview/`

### 1.6 Runner Scripts (Root Directory)
- `run_stage1_single.py`
- `run_stage2_analysis.py`
- `run_stage2_dual.py`

**Recommendation:** Consolidate into single CLI:
```python
scripts/run_analysis.py --stage=1 --phone=XXX
scripts/run_analysis.py --stage=2 --mode=weekly
scripts/run_analysis.py --stage=2 --mode=dual
```

---

## 2. FILE STRUCTURE ISSUES

### 2.1 Current Structure Problems
```
MessageAnalyzer/
├── *.py (14 files in root!)     # ❌ Too many root scripts
├── src/ (24 files)               # ❌ Flat structure
├── config/paths.py               # ✓ Good
├── data/                         # ⚠️ Needs subfolders
├── docs/                         # ✓ Good structure
└── venv/
```

### 2.2 Recommended Structure
```
MessageAnalyzer/
├── src/
│   ├── core/                     # Core analysis logic
│   │   ├── __init__.py
│   │   ├── conversation_analyzer.py
│   │   ├── llm_client.py
│   │   └── validators.py
│   ├── stage1/                   # Stage 1: Single analysis
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   │   └── evidence_parser.py
│   ├── stage2/                   # Stage 2: Weekly analysis
│   │   ├── __init__.py
│   │   ├── weekly_analyzer.py
│   │   └── citation_analyzer.py
│   ├── dashboard/                # Dashboard generation
│   │   ├── __init__.py
│   │   ├── builder.py
│   │   ├── templates/
│   │   └── components/
│   ├── extractors/               # Data extraction
│   │   ├── __init__.py
│   │   ├── conversation_extractor.py
│   │   └── contact_manager.py
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── monitoring.py
│       └── parsers.py
├── scripts/                      # User-facing CLI
│   ├── run_analysis.py
│   ├── generate_dashboard.py
│   └── extract_data.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── experimental/
├── tools/                        # Developer tools
│   ├── debug/
│   │   ├── preview_chunks.py
│   │   └── preview_prompts.py
│   └── compare/
│       └── compare_citations.py
├── config/
│   ├── __init__.py
│   ├── paths.py
│   └── settings.py
├── data/
│   ├── raw/                      # Original exports
│   ├── processed/                # Extracted conversations
│   └── output/
│       ├── conversations/        # Individual results
│       ├── dashboards/           # HTML outputs
│       ├── weekly_metrics/       # Stage 2 JSON
│       └── monitoring/           # LLM metrics
└── docs/
    ├── architecture/             # System design
    ├── algorithms/               # Technical methodology
    ├── guides/                   # User guides
    └── api/                      # Code documentation
```

---

## 2.1 Images and JSON Organization

### Current Issues
- All outputs dumped into `data/output/all_conversations/` (3847 files!)
- No separation by type (JSON, HTML, images)
- No archival/cleanup strategy

### Recommended Changes
```
data/output/
├── conversations/                # Raw conversation JSON
│   └── {phone_number}/
│       └── {timestamp}_conversation.json
├── analysis/                     # Analysis results
│   ├── stage1/
│   │   └── {phone_number}/
│   │       ├── {timestamp}_analysis.json
│   │       └── {timestamp}_evidence.json
│   └── stage2/
│       └── {phone_number}/
│           ├── weekly_metrics.json
│           └── citations.json
├── dashboards/                   # HTML outputs
│   └── {phone_number}/
│       └── {timestamp}_dashboard.html
├── images/                       # Charts, graphs, exports
│   └── {phone_number}/
│       ├── archetypes.png
│       └── sentiment_chart.png
└── archive/                      # Old/deprecated outputs
    └── {date}/
```

**Action Items:**
1. Create migration script to reorganize existing files
2. Update all path references in code
3. Add `.gitignore` entries for large output directories
4. Implement cleanup policy (archive files >30 days old)

---

## 2.2 Markdown File Organization

### Current Structure
```
./docs/algorithms/methodology_documentation.md
./docs/design/CODE_AUDIT.md
./docs/guides/LLM_MONITORING.md
./docs/guides/MessageAnalyzerRecomendation.md
./docs/guides/README_MESSAGES_EXPORT.md
./docs/guides/stage2_citation_prompts.md
./docs/guides/stage2_daily_metrics_prompt.md
./ENSEMBLE_ARCHITECTURE.md          # ❌ Should be in docs/
./PROJECT_STRUCTURE.md              # ❌ Should be in docs/
./README.md                         # ✓ OK in root
./STAGE1_MODELS_REFERENCE.md        # ❌ Should be in docs/
./STAGE2_ARCHITECTURE.md            # ❌ Should be in docs/
./TODO.md                           # ✓ OK in root
```

### Recommended Structure
```
docs/
├── architecture/                 # System design documents
│   ├── overview.md
│   ├── stage1_architecture.md
│   ├── stage2_architecture.md
│   └── ensemble_model.md
├── algorithms/                   # Technical methodology
│   ├── methodology.md
│   ├── validation_strategy.md
│   └── prompt_refinement.md
├── guides/                       # User guides & tutorials
│   ├── getting_started.md
│   ├── exporting_messages.md
│   ├── running_analysis.md
│   └── interpreting_results.md
├── reference/                    # API & configuration
│   ├── models_reference.md
│   ├── prompt_templates.md
│   ├── config_options.md
│   └── file_formats.md
├── development/                  # Developer docs
│   ├── contributing.md
│   ├── code_standards.md
│   ├── testing_strategy.md
│   └── release_process.md
└── decisions/                    # ADRs (Architecture Decision Records)
    ├── 001_llm_model_selection.md
    ├── 002_weekly_windowing.md
    └── 003_validation_approach.md
```

**Action Items:**
1. Move root-level .md files into appropriate subdirectories
2. Consolidate redundant documentation
3. Add missing sections (API docs, testing strategy)
4. Create index files for each category

---

## 2.3 Undocumented Features

### Features Lacking Documentation

1. **Weekly Metrics Validation System**
   - Location: `src/weekly_metrics_analyzer.py`
   - Missing: User guide on interpreting validation errors
   - Missing: Documentation of validation rules

2. **Meta-LLM Prompt Refinement**
   - Location: `src/weekly_metrics_analyzer.py:_refine_prompt_with_meta_llm()`
   - Missing: Algorithm explanation
   - Missing: Example failure cases and refinements

3. **Debug Panel Filtering**
   - Location: `src/add_weekly_metrics_to_dashboard.py`
   - Missing: User guide on using filters
   - Missing: What each column means

4. **Incremental Progress Saving**
   - Location: `src/weekly_metrics_analyzer.py`
   - Missing: How to resume failed analyses
   - Missing: File format specification

5. **Citation Parser**
   - Location: `src/citation_parser.py`
   - Missing: Citation format specification
   - Missing: Error handling documentation

**Action Items:**
1. Create `docs/features/` directory
2. Document each feature with:
   - Purpose & use cases
   - How it works (algorithm/approach)
   - Configuration options
   - Example outputs
   - Troubleshooting guide

---

## 2.4 Features Lacking Tests

### Critical Features Without Tests

1. **Validation System** (`src/weekly_metrics_analyzer.py`)
   - `_validate_llm_response()`
   - `_check_parseable_metrics()`
   - `_check_tone_consistency()`

   **Needed:** Unit tests for each validation rule

2. **Meta-LLM Refinement** (`src/weekly_metrics_analyzer.py`)
   - `_refine_prompt_with_meta_llm()`

   **Needed:** Integration test with mock LLM responses

3. **Dashboard Building** (`src/add_weekly_metrics_to_dashboard.py`)
   - HTML generation logic
   - Chart data preparation

   **Needed:** Template rendering tests, data validation tests

4. **Citation Extraction** (`src/citation_parser.py`)
   - Regex patterns for different citation formats

   **Needed:** Parametrized tests with various input formats

5. **Topic Summary Extraction** (`src/add_weekly_metrics_to_dashboard.py:extract_topic_summary()`)
   - Regex-based parsing

   **Needed:** Edge case tests (empty topics, malformed markdown)

### Recommended Test Structure
```python
tests/
├── unit/
│   ├── test_validators.py
│   ├── test_parsers.py
│   ├── test_citation_extraction.py
│   └── test_topic_extraction.py
├── integration/
│   ├── test_stage1_pipeline.py
│   ├── test_stage2_pipeline.py
│   └── test_dashboard_generation.py
├── fixtures/
│   ├── sample_conversations.json
│   ├── sample_llm_responses.txt
│   └── expected_outputs/
└── conftest.py
```

**Action Items:**
1. Create `tests/` directory structure
2. Add pytest configuration (`pytest.ini`)
3. Write unit tests for validation system (highest priority)
4. Add integration tests for full pipelines
5. Set up CI/CD to run tests on commit

---

## 3. UNUSED/UNCALLED FILES & FUNCTIONS

### 3.1 Potentially Unused Files

**Need Usage Analysis:**
- `compare_citation_results.py` - Is this still used?
- `analyze_conversation_distribution.py` - Active or deprecated?
- `src/categorize_relationships.py` - Called anywhere?
- `src/optimize_dashboard_ui.py` - Used or one-off script?

**Recommendation:** Run grep analysis:
```bash
# For each file, check if imported anywhere
grep -r "from.*import" --include="*.py" | grep "categorize_relationships"
```

### 3.2 Files That Changed Scope (Need Renaming)

1. **`src/llm_analyzer.py`**
   - Original: Generic LLM analysis
   - Current: Stage 1 specific
   - **Rename to:** `src/stage1/analyzer.py`

2. **`src/weekly_metrics_analyzer.py`**
   - Current: Stage 2 weekly analysis with validation
   - **Move to:** `src/stage2/weekly_analyzer.py`

3. **`src/add_weekly_metrics_to_dashboard.py`**
   - Current: Dashboard integration for weekly metrics
   - **Rename to:** `src/dashboard/add_weekly_metrics.py`

4. **`src/create_llm_dashboard.py`**
   - Current: Creates Stage 1 dashboards
   - **Rename to:** `src/dashboard/create_stage1_dashboard.py`

---

## 4. SECURITY ISSUES

### 4.1 Password/Credential Files
**Searched for:**
```bash
find . -name "*password*" -o -name "*credential*" -o -name "*.key" -o -name ".env*"
```

**Result:** No password files found in current commit

**Recommendation:**
1. Add to `.gitignore`:
   ```
   # Credentials
   .env
   .env.*
   *.key
   *_credentials.*
   secrets/
   config/credentials.json
   ```

2. Create `config/credentials.example.json` template:
   ```json
   {
     "ollama_host": "http://localhost:11434",
     "api_keys": {
       "openai": "YOUR_API_KEY_HERE"
     }
   }
   ```

3. Document in README how to set up credentials

---

## 5. CODE READABILITY & MAINTAINABILITY

### 5.1 Recommendations

1. **Add Module-Level Docstrings**
   ```python
   """
   Stage 2 Weekly Metrics Analyzer

   Analyzes conversations in weekly windows with cumulative context.
   Implements validation, retry logic, and meta-LLM prompt refinement.

   Key Features:
   - Cumulative context windows (expanding history)
   - Comprehensive validation (format, metrics, citations)
   - Automatic retry with prompt refinement
   - Incremental progress saving

   Usage:
       analyzer = WeeklyMetricsAnalyzer(model='llama3.2')
       results = analyzer.analyze_weekly(phone_number='555-1234')
   """
   ```

2. **Add Type Hints**
   ```python
   def analyze_weekly(
       self,
       phone_number: str,
       max_messages: Optional[int] = None
   ) -> Dict[str, Any]:
       """Analyze conversations in weekly windows."""
   ```

3. **Use Enums for Constants**
   ```python
   from enum import Enum

   class AnalysisStage(Enum):
       STAGE1_SINGLE = "stage1"
       STAGE2_WEEKLY = "stage2_weekly"
       STAGE2_CITATION = "stage2_citation"

   class ValidationStatus(Enum):
       VALID = "valid"
       INVALID = "invalid"
       RETRY = "retry"
   ```

4. **Extract Magic Numbers**
   ```python
   # Bad
   if retry_count < 5:

   # Good
   MAX_RETRIES = 5
   if retry_count < MAX_RETRIES:
   ```

5. **Use Dataclasses for Structured Data**
   ```python
   from dataclasses import dataclass

   @dataclass
   class ValidationResult:
       is_valid: bool
       errors: List[str]
       warnings: List[str]
       tone_consistent: bool
   ```

---

## 6. CODING STANDARDS

### 6.1 Python Standards (PEP 8)

**Current Issues:**
- Inconsistent line length (some files >120 chars)
- Mixed quote styles (single vs double)
- Inconsistent import ordering

**Recommendations:**

1. **Add `pyproject.toml`:**
   ```toml
   [tool.black]
   line-length = 100
   target-version = ['py39', 'py310', 'py311']

   [tool.isort]
   profile = "black"
   line_length = 100

   [tool.pylint]
   max-line-length = 100
   disable = ["C0111"]  # missing-docstring (we'll add them)
   ```

2. **Run Formatters:**
   ```bash
   pip install black isort pylint
   black src/
   isort src/
   pylint src/
   ```

3. **Pre-commit Hooks:**
   ```yaml
   # .pre-commit-config.yaml
   repos:
     - repo: https://github.com/psf/black
       rev: 23.3.0
       hooks:
         - id: black
     - repo: https://github.com/pycqa/isort
       rev: 5.12.0
       hooks:
         - id: isort
   ```

### 6.2 Project-Specific Standards

**Document in `docs/development/code_standards.md`:**

1. **Naming Conventions:**
   - Files: `snake_case.py`
   - Classes: `PascalCase`
   - Functions/variables: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`
   - Private methods: `_leading_underscore`

2. **Import Order:**
   ```python
   # Standard library
   import json
   from pathlib import Path

   # Third-party
   import ollama
   import pandas as pd

   # Local imports
   from config.paths import DATA_DIR
   from src.core.validators import validate_response
   ```

3. **Error Handling:**
   ```python
   # Specific exceptions
   try:
       result = analyze_conversation(phone)
   except FileNotFoundError:
       logger.error(f"Conversation file not found: {phone}")
       return None
   except ValidationError as e:
       logger.warning(f"Validation failed: {e}")
       # Retry logic
   ```

4. **Logging:**
   ```python
   import logging

   logger = logging.getLogger(__name__)

   # Not print statements
   logger.info("Starting analysis...")
   logger.warning("Validation failed, retrying...")
   logger.error("Fatal error in analysis")
   ```

---

## 7. IMPORT STANDARDS

### 7.1 Current Issues

**Absolute vs Relative Imports:**
```python
# Found in codebase - inconsistent
from src.analyze_conversation import analyze
from ..utils import helpers
import src.llm_analyzer
```

**Recommendations:**

1. **Always use absolute imports from project root:**
   ```python
   # Good
   from src.stage1.analyzer import analyze_conversation
   from src.core.validators import validate_response
   from config.paths import DATA_DIR

   # Avoid relative imports
   from ..utils import helpers  # ❌
   ```

2. **Add to `__init__.py` for cleaner imports:**
   ```python
   # src/stage2/__init__.py
   from src.stage2.weekly_analyzer import WeeklyMetricsAnalyzer
   from src.stage2.citation_analyzer import CitationAnalyzer

   __all__ = ['WeeklyMetricsAnalyzer', 'CitationAnalyzer']

   # Then use:
   from src.stage2 import WeeklyMetricsAnalyzer
   ```

3. **Ensure PYTHONPATH is set:**
   ```bash
   # In virtual environment activation or .env
   export PYTHONPATH="${PYTHONPATH}:/path/to/MessageAnalyzer"
   ```

---

## 8. DOCUMENTATION STRATEGY

### 8.1 Centralized Documentation Index

**Create `docs/INDEX.md`:**
```markdown
# MessageAnalyzer Documentation Index

## Getting Started
- [README](../README.md) - Project overview
- [Installation Guide](guides/installation.md)
- [Quick Start](guides/quick_start.md)

## User Guides
- [Exporting Messages](guides/exporting_messages.md)
- [Running Analysis](guides/running_analysis.md)
- [Interpreting Results](guides/interpreting_results.md)
- [Dashboard Features](guides/dashboard_features.md)

## Architecture
- [System Overview](architecture/overview.md)
- [Stage 1: Single Analysis](architecture/stage1.md)
- [Stage 2: Weekly Metrics](architecture/stage2.md)
- [LLM Integration](architecture/llm_integration.md)

## Technical Reference
- [File Locations](reference/file_locations.md)
- [Configuration](reference/configuration.md)
- [API Documentation](reference/api.md)
- [Model Reference](reference/models.md)
- [Prompt Templates](reference/prompts.md)

## Development
- [Code Standards](development/code_standards.md)
- [Testing Strategy](development/testing.md)
- [Contributing](development/contributing.md)
- [Release Process](development/releases.md)

## Algorithms & Methodology
- [Analysis Methodology](algorithms/methodology.md)
- [Validation Strategy](algorithms/validation.md)
- [Prompt Refinement](algorithms/prompt_refinement.md)

## Troubleshooting
- [Common Issues](guides/troubleshooting.md)
- [FAQ](guides/faq.md)
```

### 8.2 Create `docs/reference/file_locations.md`

**Complete map of where everything lives:**
```markdown
# File Locations Reference

## Scripts

### Analysis Entry Points
- **Stage 1 Analysis**: `scripts/run_analysis.py --stage=1`
- **Stage 2 Weekly**: `scripts/run_analysis.py --stage=2 --mode=weekly`
- **Dashboard Generation**: `scripts/generate_dashboard.py`

### Core Modules
- **Stage 1 Analyzer**: `src/stage1/analyzer.py`
- **Stage 2 Weekly**: `src/stage2/weekly_analyzer.py`
- **Dashboard Builder**: `src/dashboard/builder.py`
- **Validators**: `src/core/validators.py`

## Data Locations

### Input Data
- **Raw Message Exports**: `data/raw/`
- **Conversation JSON**: `data/processed/conversations/`

### Output Data
- **Analysis Results**: `data/output/analysis/`
  - Stage 1: `data/output/analysis/stage1/{phone}/`
  - Stage 2: `data/output/analysis/stage2/{phone}/`
- **Dashboards**: `data/output/dashboards/{phone}/`
- **Monitoring**: `data/output/monitoring/`

### Templates
- **HTML Templates**: `src/dashboard/templates/`
- **Prompt Templates**: `config/prompts/`

### Icons & Assets
- **Icons**: `src/dashboard/assets/icons/`
- **CSS**: `src/dashboard/assets/css/`
- **JavaScript**: `src/dashboard/assets/js/`

## Configuration

### Settings
- **Paths**: `config/paths.py`
- **Model Config**: `config/models.json`
- **Credentials**: `config/credentials.json` (not in repo)

### Ground Truth Files
- **Test Conversations**: `tests/fixtures/conversations/`
- **Expected Outputs**: `tests/fixtures/expected/`
- **Prompt Examples**: `tests/fixtures/prompts/`

## Documentation

### User Docs
- **Guides**: `docs/guides/`
- **Tutorials**: `docs/guides/tutorials/`

### Developer Docs
- **Architecture**: `docs/architecture/`
- **API Reference**: `docs/reference/api/`
- **Algorithms**: `docs/algorithms/`

### Design Decisions
- **ADRs**: `docs/decisions/`
- **Audit Reports**: `docs/audits/`
```

---

## 9. DEPENDENCY MANAGEMENT

### 9.1 Virtual Environment Check

**Current `requirements.txt`:** ✓ Exists and well-organized

**Recommendations:**

1. **Add environment validation script:**
   ```python
   # scripts/check_environment.py
   import sys
   import importlib

   REQUIRED_PACKAGES = {
       'ollama': '0.6.0',
       'torch': '2.8.0',
       'transformers': '4.56.2',
       # ... etc
   }

   def check_environment():
       """Verify all dependencies are installed."""
       missing = []
       for package, version in REQUIRED_PACKAGES.items():
           try:
               mod = importlib.import_module(package)
               if hasattr(mod, '__version__'):
                   if mod.__version__ != version:
                       print(f"⚠️  {package} version mismatch: {mod.__version__} != {version}")
           except ImportError:
               missing.append(package)

       if missing:
           print(f"❌ Missing packages: {', '.join(missing)}")
           print("Run: pip install -r requirements.txt")
           sys.exit(1)
       print("✅ Environment OK")
   ```

2. **Add to all entry-point scripts:**
   ```python
   # At top of run_analysis.py, etc.
   from scripts.check_environment import check_environment
   check_environment()
   ```

3. **Setup script:**
   ```bash
   # scripts/setup.sh
   #!/bin/bash

   # Check if venv exists
   if [ ! -d "venv" ]; then
       echo "Creating virtual environment..."
       python3 -m venv venv
   fi

   # Activate
   source venv/bin/activate

   # Install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt

   echo "✅ Setup complete"
   ```

---

## 10. FILE NAMING ON MODIFICATION

### 10.1 Current Problem
Dashboard files are being renamed with timestamps, creating duplicates:
- `0044_00649_msgs_309-948-9979_enhanced_dashboard.html`
- `0044_00649_msgs_309-948-9979_enhanced_dashboard_v2.html`
- etc.

### 10.2 Solution

**Modify `src/add_weekly_metrics_to_dashboard.py`:**
```python
def main(phone_number: str = "309-948-9979"):
    """Add weekly metrics to existing dashboard."""

    # Find EXACT dashboard file (no pattern matching)
    dashboard_file = conversations_dir / f"{phone_number}_dashboard.html"

    if not dashboard_file.exists():
        print(f"❌ Dashboard not found: {dashboard_file}")
        return

    # Read, modify, write back to SAME file
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    updated_html = add_weekly_section_to_dashboard(html_content, ...)

    # Overwrite original file
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(updated_html)

    print(f"✅ Updated: {dashboard_file}")
```

**Benefits:**
- No duplicate files
- Bookmarks don't break
- Clear which file is current
- Easy to version control

**Versioning Strategy:**
- If backup needed: Git handles it
- For manual backup: `cp dashboard.html dashboard.backup.$(date +%Y%m%d).html`
- Never auto-generate new filenames

---

## PRIORITY ACTION ITEMS

### Immediate (This Week)
1. ✅ Create todo list from audit findings
2. 🔄 Move test files to `tests/` directory
3. 🔄 Fix dashboard file overwriting (no more renaming)
4. 🔄 Add module docstrings to top 5 files

### Short-term (This Month)
5. 🔄 Reorganize data output structure
6. 🔄 Consolidate runner scripts into single CLI
7. 🔄 Write unit tests for validation system
8. 🔄 Create file locations reference doc
9. 🔄 Add type hints to public APIs

### Medium-term (This Quarter)
10. 🔄 Refactor dashboard scripts into unified builder
11. 🔄 Move all docs to proper subdirectories
12. 🔄 Set up pre-commit hooks
13. 🔄 Add integration tests
14. 🔄 Create developer onboarding guide

---

## APPENDIX: Commands for Common Tasks

```bash
# Find unused imports
pylint --disable=all --enable=unused-import src/

# Find files not imported anywhere
for file in src/*.py; do
    name=$(basename "$file" .py)
    grep -r "import.*$name" --include="*.py" . || echo "Unused: $file"
done

# Check code complexity
radon cc src/ -a -nb

# Generate dependency graph
pydeps src/weekly_metrics_analyzer.py --show-deps

# Find TODO comments
grep -r "TODO\|FIXME\|HACK" src/
```

---

**End of Audit Report**

"""
Configuration file for MessageAnalyzer project paths
"""
import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
OUTPUT_DIR = DATA_DIR / 'output'

# Source directory
SRC_DIR = PROJECT_ROOT / 'src'

# Documentation directories
DOCS_DIR = PROJECT_ROOT / 'docs'
ALGORITHMS_DOCS_DIR = DOCS_DIR / 'algorithms'
DESIGN_DOCS_DIR = DOCS_DIR / 'design'
GUIDES_DOCS_DIR = DOCS_DIR / 'guides'
SUMMARIES_DOCS_DIR = DOCS_DIR / 'summaries'

# Specific file paths
DATABASE_PATH = RAW_DATA_DIR / 'chat_copy.db'
CONVERSATIONS_DIR = OUTPUT_DIR / 'all_conversations'

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUT_DIR,
                  ALGORITHMS_DOCS_DIR, DESIGN_DOCS_DIR,
                  GUIDES_DOCS_DIR, SUMMARIES_DOCS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Ensure conversations directory exists
CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)

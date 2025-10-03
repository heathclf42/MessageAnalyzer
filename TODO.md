# Project TODO List

## High Priority

### Analysis Accuracy & Validation
- [ ] Audit keyword-based analysis methodology for accuracy
- [ ] Test analysis against known ground truth conversations
- [ ] Examine missed nuances (sarcasm, context, cultural differences)
- [ ] Validate personality type assignments with sample conversations
- [ ] Compare results with established psychological assessment tools
- [ ] Document limitations and confidence intervals for each metric
- [ ] Add validation scoring/confidence levels to analysis results
- [ ] Review false positive/negative rates in emotion detection
- [ ] Test archetype detection with edge cases

### Project Organization
- [x] Move entire project to `~/Documents/Python/Projects/MessageAnalyzer/`
- [x] Organize all images and JSON files into appropriately named folders
- [x] Organize all *.md files into folders by type:
  - [x] `docs/algorithms/` - algorithm explanations
  - [x] `docs/design/` - design decisions and plans
  - [x] `docs/summaries/` - project summaries and descriptions
  - [x] `docs/guides/` - user guides and how-tos
- [x] Update all Python scripts to use new path structure (config/paths.py)

### Dashboard Enhancements
- [x] Add radar charts showing top 7 archetypes for each person to individual dashboards
- [ ] Add collapsible/expandable methodology section to individual dashboards
- [x] Fix Messages tab visibility issue (messages not displaying despite no console errors)

### Testing & Validation
- [ ] Test master dashboard network graph with different display limits
- [ ] Test sorting options respect display limits correctly
- [ ] Verify whitespace calculation works properly with various conversation counts
- [ ] Create tests for all features and capabilities that lack them

## Medium Priority

### Academic & Professional Analysis Review
- [ ] Examine psychological profiling from academic perspective
  - [ ] What methodologies would psychologists/researchers use?
  - [ ] What additional views/breakdowns are missing?
  - [ ] What statistical measures should be included? (confidence intervals, p-values, effect sizes)
  - [ ] What conversation features are overlooked? (turn-taking, topic shifts, power dynamics)
- [ ] Research existing LLMs for psychological analysis
  - [ ] Identify LLMs fine-tuned for sentiment/personality analysis
  - [ ] Evaluate local deployment options (Llama, Mistral, etc.)
  - [ ] Compare accuracy: keyword-based vs transformer-based approaches
  - [ ] Research NLP models for conversation analysis (BERT, RoBERTa variants)
- [ ] Identify missing professional insights
  - [ ] Discourse analysis patterns (coherence, topic management)
  - [ ] Psycholinguistic features (lexical diversity, syntactic complexity)
  - [ ] Temporal dynamics (conversation rhythm, response latency patterns)
  - [ ] Social network analysis metrics (centrality, clustering)
  - [ ] Pragmatic analysis (speech acts, politeness strategies)

### UI/UX Data Linking & Interactivity
- [x] Enhance data connections in dashboards
  - [x] Add hover tooltips showing detailed stats on graphs (network nodes)
  - [ ] Link archetype scores to evidence messages (clickable)
  - [ ] Cross-link between timeline and emotion charts
  - [x] Add drill-down from master network to individual conversations (clickable nodes)
  - [ ] Connect relationship scores to supporting metrics
- [ ] Augment existing visualizations
  - [x] Hovering over network nodes shows conversation preview (tooltips with name, messages, type, archetype, MBTI)
  - [ ] Clicking emotion chart points filters messages by date
  - [ ] Link MBTI/Enneagram to archetype distribution
  - [ ] Add correlation matrix between psychological metrics
  - [ ] Create relationship comparison overlay (compare 2+ people)

### Documentation
- [ ] Create user guide for navigating dashboards
- [ ] Document export features (JSON/TXT)
- [ ] Add examples of interpreting relationship scores

### Code Quality & Standards
- [ ] Review division by zero errors in small conversation dashboards
- [ ] Add error handling for edge cases
- [ ] Optimize performance for large conversation sets (>1000)
- [x] Review files for similar names, redundancy, or duplicated functionality
- [x] Identify and delete unused/uncalled files or functions
- [x] Rename files that changed/grew in scope
- [x] Remove multiple password files (consolidate if needed) - None found
- [x] Review and fix all import statements (Python path, relative vs absolute)
- [ ] Ensure virtual environment setup with dependency checking

### Code Documentation & Standards
- [ ] Add/expand docstrings for all public methods (include args & return types)
- [ ] Add type hints to all function/method signatures
- [ ] Add docstrings for all private methods with non-trivial logic
- [ ] Add/expand module-level docstrings where missing
- [ ] Add inline comments for non-obvious logic or calculations
- [x] Create project architecture documentation (PROJECT_STRUCTURE.md)
- [x] Document code locations, best practices, and design decisions
- [x] Document template locations, icons, ground truth files, etc.
- [x] Ensure all features/capabilities are documented
- [ ] Verify Python coding standards (PEP 8) compliance

## Low Priority

### Feature Ideas
- [ ] Add emoji analysis to emotion detection
- [ ] Implement emotional intensity detection (happy vs ecstatic)
- [ ] Add comparison view (compare 2+ relationships side by side)
- [ ] Export master dashboard data to CSV
- [ ] Add date range filtering

### UI/UX Improvements
- [ ] Add keyboard shortcuts for navigation
- [ ] Implement dark mode toggle
- [ ] Add print-friendly CSS

## Completed ✓

### Recent Code Cleanup (Oct 2, 2025)
- [x] Deleted 7 deprecated files (44% reduction in codebase)
- [x] Fixed broken import in add_contact_names.py
- [x] Renamed 4 files with clearer, function-based names
- [x] Created CODE_AUDIT.md documenting all changes
- [x] Eliminated ~3,000 lines of redundant code

### Dashboard Features
- [x] Created message viewer dashboard with full conversation history
- [x] Added search functionality to message viewer
- [x] Added export capabilities (JSON and TXT)
- [x] Created methodology documentation
- [x] Added sorting options to master dashboard (14 different sorts)
- [x] Fixed navigation to not open new tabs
- [x] Added back button to return to main dashboard
- [x] Made network graph searchable
- [x] Fixed network line lengths (fewer messages = shorter lines)
- [x] Changed network background to light gray
- [x] Fixed relationship score loading in master dashboard
- [x] Fixed network graph whitespace calculation
- [x] Fixed contact filtering to respect display limits when sorting
- [x] Batch regenerated all dashboards with enhanced features

### Recent Updates (Current Session)
- [x] Updated all Python scripts to use config/paths.py (centralized path management)
- [x] Tested all scripts with new directory structure
- [x] Added radar charts for top 7 archetypes to individual dashboards
- [x] Fixed Messages tab visibility issue (added DOMContentLoaded initialization)
- [x] Improved text readability in network graph (dark stroke outline on labels)
- [x] Added hover tooltips to network nodes (shows name, messages, type, date range, archetype, MBTI)
- [x] Added hover effects to network nodes (brightness increase, thicker stroke)
- [x] Regenerated all 768 individual dashboards with radar charts
- [x] Regenerated master dashboard with text readability and tooltip improvements

---

**Last Updated:** 2025-10-02

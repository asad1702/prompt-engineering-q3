# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Applications

**Console-based Analysis:**
```bash
python run_beam_analysis.py
```

**Streamlit Web Interface:**
```bash
# Standard prompt analyzer
streamlit run streamlit_prompt_analyzer.py

# Strategic prompt analyzer
streamlit run strategic_prompt_analyzer.py
```

**Workspace Analyzer GUI:**
```bash
python workspace_analyzer_gui.py
```

### Dependencies Installation

```bash
# For console applications
pip install -r requirements.txt

# For Streamlit applications
pip install -r requirements_streamlit.txt
```

## Architecture Overview

This repository contains a suite of prompt analysis tools designed for solution engineering teams working with Beam conventions and prompt recipes.

### Core Components

1. **beam_convention_analyzer.py**: Core analyzer for Beam-specific conventions including Topic/EndTopic patterns, context blocks, variable patterns, and anti-hallucination measures.

2. **strategic_prompt_analyzer.py**: Enhanced Streamlit-based strategic analyzer with:
   - Pattern Discovery Engine for detecting all prompt conventions
   - Interactive Template Builder for standardization
   - Workshop Facilitation Module for team collaboration
   - Comprehensive pattern analysis and visualization

3. **streamlit_prompt_analyzer.py**: Web-based interface for workspace and prompt analysis with interactive visualizations.

4. **workspace_analyzer.py**: Core workspace analysis functionality for examining prompt collections.

5. **workspace_analyzer_gui.py**: GUI version of the workspace analyzer.

### Data Format

The analyzers expect JSON files containing prompt data, typically named "Prompt Recipies - Prompts.json". The data structure should include prompt text and metadata fields like owner, project, and creation date.

### Key Analysis Features

- Pattern detection for Beam conventions (Topic/EndTopic, context blocks, variables)
- Quality metrics (complexity, clarity, tone, structure scores)
- Statistical analysis and visualizations
- Export functionality (JSON/CSV)
- Interactive filtering and search capabilities

### Enhanced Features in Strategic Analyzer

- **Pattern Discovery Engine**: Detects XML tags, @ symbols, variable formats, naming conventions
- **Template Builder**: Interactive design tool for creating standardized prompt templates
- **Workshop Module**: Facilitates team collaboration on convention selection and standardization
- **Convention Voting**: Side-by-side comparison and voting on preferred patterns
- **Template Export**: Multiple formats (JSON, YAML, Markdown) for team distribution

The tools are designed to help teams standardize prompt creation, identify best practices, and improve prompt quality across projects. The strategic analyzer now provides a complete workflow from pattern discovery through template standardization to team adoption.
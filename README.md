# Strategic Prompt Analyzer for Beam Solution Engineers

A comprehensive suite of tools designed to analyze, standardize, and improve prompt engineering practices for Beam Solution Engineers. This project provides actionable insights, pattern discovery, and collaborative tools for prompt optimization.

## 🎯 Overview

The Strategic Prompt Analyzer is a Streamlit-based application that helps teams:
- Analyze prompt quality and convention usage
- Discover patterns across prompt collections
- Build standardized templates
- Facilitate team workshops for convention adoption
- Track and improve prompt engineering practices

## 🚀 Features

### 1. **Quality Dashboard** 
- Real-time analysis of prompt conventions and best practices
- Visual metrics for convention adoption rates
- Workspace-specific insights
- Automated quality issue detection
- Strategic recommendations for improvement

### 2. **Pattern Discovery Engine**
- Automatic detection of XML tags, @ symbols, and variable formats
- Analysis of naming conventions (camelCase, snake_case, etc.)
- Section header identification
- Cross-workspace pattern comparison
- Comprehensive pattern aggregation

### 3. **Template Builder**
- Interactive template design interface
- Customizable sections with required/optional flags
- Multiple export formats (JSON, YAML, Markdown)
- Real-time preview with different tag styles
- Version control for templates

### 4. **Workshop Facilitation Module**
- Collaborative decision-making tools
- Convention voting system
- Template structure discussions
- Decision logging and tracking
- Export workshop reports

## 📊 Key Conventions Tracked

### Structure & Organization
- **Context Blocks**: `<Context>API Integration</Context>` - Structured context sections
- **Role Definitions**: `Role: You are a data analyst` - Clear AI role specification
- **Instruction Sections**: `Instructions: Analyze the data` - Task clarity

### Content & Clarity
- **Variable Definitions**: `Variables: userInput, outputFormat` - Input specification
- **Output Formats**: `Output Format: JSON` - Response structure
- **Examples Provided**: `Example: {"name": "John"}` - Learning from examples

### Quality & Safety
- **Anti-Hallucination**: `Do not hallucinate` - Prevent AI from making things up
- **Step-by-Step**: `Step 1: Analyze, Step 2: Validate` - Break down complex tasks
- **Constraints**: `Constraints: Max 100 words` - Set boundaries

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Dependencies Installation

```bash
# Install required packages
pip install streamlit pandas plotly numpy

# Or use requirements file (if available)
pip install -r requirements_streamlit.txt
```

## 🏃‍♂️ Running the Application

```bash
# Run the Strategic Prompt Analyzer
streamlit run strategic_prompt_analyzer.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📁 Data Format

The analyzer expects JSON files containing prompt data with the following structure:

```json
[
  {
    "prompt": "Your prompt content here...",
    "workspace_name": "Workspace A",
    "owner": "John Doe",
    "project": "Project Name",
    "created_date": "2024-01-15"
  },
  ...
]
```

**Required field**: `prompt` - Contains the actual prompt text to analyze

**Optional fields**: 
- `workspace_name` - For workspace-specific analysis
- Additional metadata fields for filtering and reporting

## 📈 Usage Workflow

1. **Upload Data**
   - Upload your prompt JSON file via the sidebar
   - System validates the file structure automatically

2. **Quality Dashboard**
   - Review convention usage metrics
   - Identify quality issues and best practices
   - Focus on strategic recommendations

3. **Pattern Discovery**
   - Explore discovered patterns in your prompts
   - Analyze XML tags, variable formats, and naming conventions
   - Compare patterns across workspaces

4. **Template Builder**
   - Create standardized templates based on discovered patterns
   - Customize sections and formatting
   - Export templates for team distribution

5. **Workshop Module**
   - Start a workshop session
   - Vote on conventions and patterns
   - Document decisions
   - Export workshop reports

## 📊 Metrics and Analysis

### Convention Usage Analysis
- Percentage of prompts using each convention
- Category-based grouping (Structure, Clarity, Safety)
- Importance levels (Critical, High, Medium)
- Visual charts and progress indicators

### Complexity Metrics
- Average prompt length
- Section count distribution
- Tag density (tags per 1000 characters)
- Instruction density analysis

### Pattern Discovery Metrics
- Unique XML tags count
- Variable format distribution
- Section header frequency
- Naming convention adoption

## 🎯 Best Practices

### For High-Quality Prompts:
1. **Always include role definitions** - Specify the AI's role clearly
2. **Use structured sections** - XML tags or clear headers
3. **Add anti-hallucination instructions** - Prevent invented information
4. **Provide examples** - Show expected inputs and outputs
5. **Define constraints** - Set clear boundaries
6. **Use step-by-step instructions** - Break down complex tasks

### For Team Standardization:
1. **Regular analysis** - Track convention adoption monthly
2. **Workshop sessions** - Collaborate on standards
3. **Template distribution** - Share approved templates
4. **Training focus** - Address low-adoption conventions
5. **Cross-workspace sharing** - Learn from high performers

## 📤 Export Options

- **Quality Reports** (JSON) - Comprehensive analysis results
- **Convention Data** (CSV) - Usage statistics
- **Templates** (JSON/YAML/Markdown) - Standardized formats
- **Workshop Reports** (JSON/Markdown) - Decision documentation

## 🔧 Advanced Features

### Pattern Discovery Engine
- Regex-based pattern matching
- Multi-format variable detection
- Naming convention analysis
- Hierarchical pattern aggregation

### Template Customization
- Drag-and-drop section ordering (UI placeholder)
- Mixed tag style support
- Custom variable formats
- Version control integration

### Workshop Facilitation
- Real-time voting system
- Decision logging
- Participant tracking
- Automated report generation

## 🐛 Troubleshooting

### Common Issues:
1. **"No prompts found"** - Ensure JSON contains 'prompt' field with content
2. **Invalid JSON format** - Verify file is a JSON array of objects
3. **Missing conventions** - Check prompt content for expected patterns
4. **Export failures** - Ensure write permissions in download directory

## 🤝 Contributing

This tool is designed for Beam Solution Engineers. For feature requests or bug reports:
1. Document the issue clearly
2. Include sample data (anonymized)
3. Suggest expected behavior
4. Contact the development team

## 📝 License

Internal use only for Beam Solution Engineering teams.

---

**💡 Pro Tip**: Start with the Quality Dashboard to get immediate insights, then dive deeper with Pattern Discovery to understand your team's prompt engineering practices!
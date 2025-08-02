# Prompt Analysis Engine for Solution Engineering Team

A comprehensive Python-based analysis engine for analyzing prompt recipes and generating insights for solution engineering teams.

## 🚀 Features

### Core Analysis Capabilities
- **CSV Data Loading**: Automatically reads and parses CSV files containing prompt data
- **Pattern Detection**: Identifies prompting conventions, instructions, examples, constraints, and output formats
- **Quality Metrics**: Calculates complexity, clarity, tone, and structure scores
- **Statistical Analysis**: Provides comprehensive statistics on prompt characteristics
- **Filtering & Search**: Filter prompts by owner, project, length, patterns, and keywords
- **Export Functionality**: Export results in JSON or CSV formats

### Analysis Types
1. **Prompting Conventions**: Analyzes pattern usage and consistency
2. **Structure Quality**: Evaluates prompt structure and organization
3. **Tone Consistency**: Assesses tone uniformity across prompts
4. **Optimization Suggestions**: Provides actionable improvement recommendations
5. **Comprehensive Analysis**: Combines all analysis types

## 📋 Requirements

- Python 3.7+
- Required packages (see `requirements.txt`):
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - pathlib2

## 🛠️ Installation

1. **Clone or download the project files**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 📊 Usage

### Quick Start

1. **Place your CSV file** in the project directory
   - Expected filename: `"Prompt Recipes - agent_prompts (input).csv"`
   - Or use the interactive interface to specify a different path

2. **Run the analysis**:
   ```bash
   python run_analysis.py
   ```

3. **Choose your analysis mode**:
   - Option 1: Run example analysis (requires CSV file)
   - Option 2: Run interactive interface
   - Option 3: Exit

### Interactive Interface

Run the interactive interface for step-by-step analysis:

```bash
python prompt_analysis_engine.py
```

The interactive interface provides:
- CSV file loading and preview
- Multiple analysis types
- Filtering options
- Export capabilities

### Programmatic Usage

```python
from prompt_analysis_engine import PromptAnalysisEngine

# Initialize the engine
engine = PromptAnalysisEngine("your_prompts.csv")

# Display data preview
engine.display_data_preview()

# Analyze all prompts
engine.analyze_all_prompts()

# Generate specific insights
conventions = engine.generate_insights('prompting_conventions')
structure = engine.generate_insights('structure_quality')
tone = engine.generate_insights('tone_consistency')
suggestions = engine.generate_insights('optimization_suggestions')

# Filter prompts
filtered_results = engine.filter_by_criteria({
    'owner': 'John Doe',
    'min_words': 20,
    'max_words': 100,
    'pattern': 'instructions'
})

# Export results
engine.export_results(engine.analysis_results, 'results.json', 'json')
```

## 📈 Analysis Metrics

### Pattern Detection
- **Instructions**: "please", "you should", "follow these steps", etc.
- **Examples**: "example:", "for instance", "such as", etc.
- **Constraints**: "do not", "never", "only", "must", etc.
- **Output Format**: "respond in", "format your response", etc.
- **Role Definition**: "you are a", "act as a", "expert in", etc.

### Quality Scores
- **Complexity Score**: Based on word length, sentence complexity, and technical terms
- **Clarity Score**: Based on sentence length, pattern presence, and structure
- **Tone Score**: Consistency and appropriateness of tone indicators
- **Structure Score**: Organization, pattern diversity, and length appropriateness
- **Readability Score**: Flesch Reading Ease approximation

### Keyword Categories
- **Action Keywords**: analyze, create, generate, explain, etc.
- **Technical Keywords**: api, database, system, architecture, etc.
- **Business Keywords**: strategy, process, workflow, efficiency, etc.

## 🔍 Filtering Options

Filter prompts by:
- **Owner**: Specific prompt author
- **Project**: Live project name
- **Word Count**: Minimum/maximum word limits
- **Patterns**: Specific pattern types
- **Keywords**: Action, technical, or business keywords

## 📤 Export Formats

### JSON Export
```json
{
  "prompt_id": "prompt_1",
  "prompt_text": "Your prompt content...",
  "metrics": {
    "word_count": 45,
    "complexity_score": 3.2,
    "clarity_score": 7.8,
    "patterns_found": ["instructions", "examples"],
    "keywords": ["action:analyze", "technical:api"]
  },
  "metadata": {
    "owner": "John Doe",
    "project": "Project Alpha"
  }
}
```

### CSV Export
Flattened format with all metrics and metadata in columns for easy spreadsheet analysis.

## 🎯 Use Cases

### For Solution Engineering Teams
1. **Quality Assurance**: Identify prompts that need improvement
2. **Consistency Analysis**: Ensure uniform prompting standards
3. **Best Practice Identification**: Find effective prompt patterns
4. **Training Material**: Use insights for team training
5. **Process Optimization**: Standardize prompt creation workflows

### For Q3 Planning
1. **Baseline Assessment**: Understand current prompt quality
2. **Gap Analysis**: Identify areas for improvement
3. **Success Metrics**: Track improvements over time
4. **Template Development**: Create standardized prompt templates
5. **Team Training**: Develop training materials based on analysis

## 🔧 Customization

### Adding New Patterns
```python
# In PromptAnalyzer class
self.patterns['custom_patterns'] = [
    r'your\s+custom\s+pattern',
    r'another\s+pattern'
]
```

### Adding New Keywords
```python
# In PromptAnalyzer class
self.keywords['custom_category'] = [
    'keyword1', 'keyword2', 'keyword3'
]
```

### Custom Scoring
Modify the scoring functions in the `PromptAnalyzer` class:
- `_calculate_complexity_score()`
- `_calculate_clarity_score()`
- `_calculate_tone_score()`
- `_calculate_structure_score()`

## 🚀 Future Extensions

The modular design supports future enhancements:
- **AI-Assisted Grading**: Integrate with LLM APIs for automated assessment
- **Classification Models**: Machine learning-based prompt categorization
- **Performance Tracking**: Link prompt quality to AI response quality
- **Collaborative Features**: Multi-user analysis and commenting
- **Visualization Dashboard**: Web-based interface with charts and graphs

## 📝 Example Output

```
🚀 Prompt Analysis Engine for Solution Engineering Team
============================================================
✅ Successfully loaded 150 prompts from CSV
📊 Columns found: ['prompt', 'owner', 'project', 'date_created']

📋 PROMPTING CONVENTIONS:
- Most common pattern: instructions
- Pattern diversity: 4
- Instructions usage: 85.3%
- Examples usage: 42.0%

🏗️ STRUCTURE QUALITY:
- Average words: 67.2
- Average structure score: 6.8
- Average clarity score: 7.2

🎭 TONE CONSISTENCY:
- Average tone score: 6.5
- Tone consistency: True
- Recommended tone: neutral

💡 OPTIMIZATION SUGGESTIONS:
- Length Optimization:
  • Consider standardizing prompt length
- Structure Improvements:
  • Add more structural elements like clear sections
```

## 🤝 Contributing

This tool is designed for solution engineering teams. Feel free to:
- Add new analysis types
- Improve scoring algorithms
- Add new export formats
- Enhance the user interface

## 📞 Support

For questions or issues:
1. Check the CSV file format and column names
2. Ensure all dependencies are installed
3. Review the error messages for specific issues
4. Use the interactive interface for step-by-step troubleshooting # prompt-engineering-q3

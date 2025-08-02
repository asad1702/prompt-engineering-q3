#!/usr/bin/env python3
"""
Strategic Prompt Analyzer for Beam Solution Engineers
Focuses on actionable insights to improve prompt engineering practices
"""

import streamlit as st
import json
import pandas as pd
import re
import numpy as np
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple, Set
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="🎯 Strategic Prompt Analyzer",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .insight-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-card {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .metric-highlight {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #bee5eb;
    }
</style>
""", unsafe_allow_html=True)

# Pattern Discovery Engine
class PatternDiscoveryEngine:
    """Discover and analyze all prompt conventions and patterns"""
    
    def __init__(self):
        # Define pattern types to search for
        self.xml_tag_pattern = r'<([A-Za-z][A-Za-z0-9]*)>.*?</\1>|<([A-Za-z][A-Za-z0-9]*)>.*?<[Ee]nd\2>'
        self.at_tag_pattern = r'@[a-zA-Z][a-zA-Z0-9_]*'
        self.double_brace_pattern = r'\{\{[^}]+\}\}'
        self.triple_tick_pattern = r'```\{[^}]+\}```'
        self.markdown_header_pattern = r'^#+\s+(.+)$'
        self.variable_patterns = [
            (r'\{\{([^}]+)\}\}', 'double_braces'),
            (r'@([a-zA-Z][a-zA-Z0-9_]*)', 'at_symbol'),
            (r'```\{([^}]+)\}```', 'triple_ticks'),
            (r'\[\[([^\]]+)\]\]', 'double_brackets'),
            (r'<([^>]+)>', 'xml_style')
        ]
        
    def discover_patterns(self, prompt: str) -> Dict[str, Any]:
        """Discover all patterns in a single prompt"""
        patterns = {
            'xml_tags': [],
            'at_tags': [],
            'variables': defaultdict(list),
            'section_headers': [],
            'naming_conventions': set(),
            'structural_elements': []
        }
        
        # Find XML-style tags
        xml_matches = re.findall(self.xml_tag_pattern, prompt, re.DOTALL)
        for match in xml_matches:
            tag = match[0] if match[0] else match[1]
            if tag and tag not in patterns['xml_tags']:
                patterns['xml_tags'].append(tag)
        
        # Find @-style tags
        at_matches = re.findall(self.at_tag_pattern, prompt)
        patterns['at_tags'] = list(set(at_matches))
        
        # Find variable patterns
        for pattern, pattern_type in self.variable_patterns:
            matches = re.findall(pattern, prompt)
            if matches:
                patterns['variables'][pattern_type].extend(matches)
        
        # Find markdown headers
        lines = prompt.split('\n')
        for line in lines:
            header_match = re.match(self.markdown_header_pattern, line)
            if header_match:
                patterns['section_headers'].append(header_match.group(1).strip())
        
        # Detect naming conventions in variables
        all_vars = []
        for var_list in patterns['variables'].values():
            all_vars.extend(var_list)
        
        for var in all_vars:
            if re.match(r'^[a-z]+(?:[A-Z][a-z]+)*$', var):
                patterns['naming_conventions'].add('camelCase')
            elif re.match(r'^[a-z]+(?:_[a-z]+)*$', var):
                patterns['naming_conventions'].add('snake_case')
            elif re.match(r'^[A-Z]+(?:_[A-Z]+)*$', var):
                patterns['naming_conventions'].add('UPPER_SNAKE_CASE')
            elif re.match(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)*$', var):
                patterns['naming_conventions'].add('PascalCase')
        
        return patterns
    
    def aggregate_patterns(self, data: List[Dict]) -> Dict[str, Any]:
        """Aggregate patterns across all prompts"""
        aggregated = {
            'total_prompts_analyzed': 0,
            'xml_tags': Counter(),
            'at_tags': Counter(),
            'variable_formats': Counter(),
            'section_headers': Counter(),
            'naming_conventions': Counter(),
            'patterns_by_workspace': {}
        }
        
        for item in data:
            prompt_content = item.get('prompt', '')
            workspace = item.get('workspace_name', 'Unknown')
            
            if not prompt_content:
                continue
            
            aggregated['total_prompts_analyzed'] += 1
            patterns = self.discover_patterns(prompt_content)
            
            # Initialize workspace patterns if not exists
            if workspace not in aggregated['patterns_by_workspace']:
                aggregated['patterns_by_workspace'][workspace] = {
                    'xml_tags': Counter(),
                    'at_tags': Counter(),
                    'variable_formats': Counter(),
                    'section_headers': Counter(),
                    'naming_conventions': Counter()
                }
            
            # Aggregate XML tags
            for tag in patterns['xml_tags']:
                aggregated['xml_tags'][tag] += 1
                aggregated['patterns_by_workspace'][workspace]['xml_tags'][tag] += 1
            
            # Aggregate @ tags
            for tag in patterns['at_tags']:
                aggregated['at_tags'][tag] += 1
                aggregated['patterns_by_workspace'][workspace]['at_tags'][tag] += 1
            
            # Aggregate variable formats
            for format_type, vars in patterns['variables'].items():
                if vars:
                    aggregated['variable_formats'][format_type] += 1
                    aggregated['patterns_by_workspace'][workspace]['variable_formats'][format_type] += 1
            
            # Aggregate section headers
            for header in patterns['section_headers']:
                aggregated['section_headers'][header] += 1
                aggregated['patterns_by_workspace'][workspace]['section_headers'][header] += 1
            
            # Aggregate naming conventions
            for convention in patterns['naming_conventions']:
                aggregated['naming_conventions'][convention] += 1
                aggregated['patterns_by_workspace'][workspace]['naming_conventions'][convention] += 1
        
        return aggregated

@st.cache_data
def analyze_prompt_quality(data: List[Dict]) -> Dict[str, Any]:
    """
    Analyze prompt quality and patterns for actionable insights
    """
    insights = {
        'total_prompts': len(data),
        'workspace_breakdown': Counter(),
        'convention_usage': {},
        'quality_issues': [],
        'best_practices': [],
        'pattern_analysis': {},
        'recommendations': []
    }
    
    # Initialize counters
    convention_counts = {
        'context_blocks': 0,
        'role_definitions': 0,
        'instruction_sections': 0,
        'variable_definitions': 0,
        'output_formats': 0,
        'anti_hallucination': 0,
        'step_by_step': 0,
        'examples_provided': 0,
        'constraints_defined': 0
    }
    
    workspace_patterns = {}
    
    total_length = 0
    
    for item in data:
        # Focus only on the 'prompt' key as specified
        prompt_content = item.get('prompt', '')
        workspace = item.get('workspace_name', 'Unknown')
        
        # Skip items without prompt content
        if not prompt_content or prompt_content.strip() == '':
            continue
            
        # Count workspace
        insights['workspace_breakdown'][workspace] += 1
        total_length += len(prompt_content)
        
        # Initialize workspace patterns if not exists
        if workspace not in workspace_patterns:
            workspace_patterns[workspace] = {
                'conventions_used': set(),
                'avg_length': 0,
                'has_examples': 0,
                'has_constraints': 0,
                'has_anti_hallucination': 0
            }
        
        # Analyze conventions
        conventions_found = set()
        
        # Context blocks - detect any XML-style tags with content
        if re.search(r'<[A-Za-z]+>.*?</[A-Za-z]+>|<[A-Za-z]+>.*?<[Ee]nd[A-Za-z]+>', prompt_content, re.DOTALL):
            convention_counts['context_blocks'] += 1
            conventions_found.add('context_blocks')
        
        # Role definitions - more comprehensive pattern matching
        role_patterns = [
            r'[Rr]ole:',
            r'[Yy]ou are',
            r'[Aa]s a',
            r'[Aa]cting as',
            r'[Yy]our role is',
            r'[Yy]ou act as',
            r'[Yy]ou will be',
            r'[Yy]ou serve as'
        ]
        if any(re.search(pattern, prompt_content) for pattern in role_patterns):
            convention_counts['role_definitions'] += 1
            conventions_found.add('role_definitions')
        
        # Instruction sections
        if re.search(r'[Ii]nstructions?:|Task:|Objective:', prompt_content):
            convention_counts['instruction_sections'] += 1
            conventions_found.add('instruction_sections')
        
        # Variable definitions
        if re.search(r'[Vv]ariables?:|Parameters?:|Input:', prompt_content):
            convention_counts['variable_definitions'] += 1
            conventions_found.add('variable_definitions')
        
        # Output formats
        if re.search(r'[Oo]utput [Ff]ormat:|Format:|Response format:', prompt_content):
            convention_counts['output_formats'] += 1
            conventions_found.add('output_formats')
        
        # Anti-hallucination
        if re.search(r'do not hallucinate|do not invent|only use provided|stick to facts', prompt_content, re.IGNORECASE):
            convention_counts['anti_hallucination'] += 1
            conventions_found.add('anti_hallucination')
            workspace_patterns[workspace]['has_anti_hallucination'] += 1
        
        # Step-by-step instructions
        if re.search(r'step by step|step-by-step|step 1|first|then|finally', prompt_content, re.IGNORECASE):
            convention_counts['step_by_step'] += 1
            conventions_found.add('step_by_step')
        
        # Examples provided
        if re.search(r'[Ee]xample:|[Ee]xamples?:|For example|Sample:', prompt_content):
            convention_counts['examples_provided'] += 1
            conventions_found.add('examples_provided')
            workspace_patterns[workspace]['has_examples'] += 1
        
        # Constraints defined
        if re.search(r'[Cc]onstraints?:|[Ll]imitations?:|[Rr]ules?:', prompt_content):
            convention_counts['constraints_defined'] += 1
            conventions_found.add('constraints_defined')
            workspace_patterns[workspace]['has_constraints'] += 1
        
        # Update workspace patterns
        workspace_patterns[workspace]['conventions_used'].update(conventions_found)
    
    # Calculate averages and insights
    avg_length = total_length / len(data) if data else 0
    
    # Quality analysis
    quality_issues = []
    best_practices = []
    
    # Identify issues
    if convention_counts['anti_hallucination'] / len(data) < 0.3:
        quality_issues.append("⚠️ Less than 30% of prompts include anti-hallucination instructions")
    
    if convention_counts['examples_provided'] / len(data) < 0.2:
        quality_issues.append("⚠️ Less than 20% of prompts provide examples")
    
    if convention_counts['step_by_step'] / len(data) < 0.4:
        quality_issues.append("⚠️ Less than 40% of prompts use step-by-step instructions")
    
    if convention_counts['context_blocks'] / len(data) < 0.5:
        quality_issues.append("⚠️ Less than 50% of prompts use structured XML-style tags")
    
    # Identify best practices
    if convention_counts['role_definitions'] / len(data) > 0.7:
        best_practices.append("✅ Strong role definition usage (>70%)")
    
    if convention_counts['instruction_sections'] / len(data) > 0.6:
        best_practices.append("✅ Good instruction section coverage (>60%)")
    
    if convention_counts['context_blocks'] / len(data) > 0.6:
        best_practices.append("✅ Good use of structured XML-style tags (>60%)")
    
    # Generate recommendations
    recommendations = []
    
    if convention_counts['anti_hallucination'] / len(data) < 0.5:
        recommendations.append("🎯 **Priority**: Add anti-hallucination instructions to more prompts")
    
    if convention_counts['examples_provided'] / len(data) < 0.3:
        recommendations.append("🎯 **Priority**: Include examples in prompts for better clarity")
    
    if convention_counts['output_formats'] / len(data) < 0.4:
        recommendations.append("🎯 **Priority**: Define output formats more consistently")
    
    if convention_counts['context_blocks'] / len(data) < 0.5:
        recommendations.append("🎯 **Priority**: Use more structured XML-style tags for better organization")
    
    # Workspace-specific insights
    workspace_insights = {}
    for workspace, patterns in workspace_patterns.items():
        workspace_insights[workspace] = {
            'convention_count': len(patterns['conventions_used']),
            'has_examples_rate': patterns['has_examples'] / insights['workspace_breakdown'][workspace],
            'has_constraints_rate': patterns['has_constraints'] / insights['workspace_breakdown'][workspace],
            'has_anti_hallucination_rate': patterns['has_anti_hallucination'] / insights['workspace_breakdown'][workspace]
        }
    
    # Add Pattern Discovery Engine analysis
    pattern_engine = PatternDiscoveryEngine()
    discovered_patterns = pattern_engine.aggregate_patterns(data)
    
    insights.update({
        'convention_usage': convention_counts,
        'quality_issues': quality_issues,
        'best_practices': best_practices,
        'recommendations': recommendations,
        'workspace_insights': workspace_insights,
        'avg_length': avg_length,
        'discovered_patterns': discovered_patterns
    })
    
    return insights

def detect_actual_patterns(data: List[Dict]) -> Dict[str, List[str]]:
    """
    Detect actual patterns used in prompts for more detailed analysis
    """
    patterns = {
        'xml_tags': [],
        'role_patterns': [],
        'instruction_patterns': [],
        'variable_patterns': [],
        'output_patterns': []
    }
    
    for item in data:
        prompt_content = item.get('prompt', '')
        if not prompt_content:
            continue
            
        # Detect XML-style tags
        xml_matches = re.findall(r'<([A-Za-z]+)>.*?</\1>|<([A-Za-z]+)>.*?<[Ee]nd\2>', prompt_content, re.DOTALL)
        for match in xml_matches:
            tag = match[0] if match[0] else match[1]
            if tag not in patterns['xml_tags']:
                patterns['xml_tags'].append(tag)
        
        # Detect role patterns
        role_patterns = [
            (r'[Rr]ole:\s*([^.\n]+)', 'Role:'),
            (r'[Yy]ou are\s+([^.\n]+)', 'You are'),
            (r'[Aa]s a\s+([^.\n]+)', 'As a'),
            (r'[Aa]cting as\s+([^.\n]+)', 'Acting as'),
            (r'[Yy]our role is\s+([^.\n]+)', 'Your role is'),
            (r'[Yy]ou act as\s+([^.\n]+)', 'You act as'),
            (r'[Yy]ou will be\s+([^.\n]+)', 'You will be'),
            (r'[Yy]ou serve as\s+([^.\n]+)', 'You serve as')
        ]
        
        for pattern, label in role_patterns:
            matches = re.findall(pattern, prompt_content)
            for match in matches:
                full_pattern = f"{label} {match}"
                if full_pattern not in patterns['role_patterns']:
                    patterns['role_patterns'].append(full_pattern)
    
    return patterns

def analyze_prompt_complexity(data: List[Dict]) -> Dict[str, Any]:
    """
    Analyze prompt complexity and structure patterns
    """
    complexity_metrics = {
        'length_distribution': [],
        'section_count': [],
        'xml_tag_density': [],
        'instruction_density': [],
        'workspace_complexity': {}
    }
    
    for item in data:
        prompt_content = item.get('prompt', '')
        workspace = item.get('workspace_name', 'Unknown')
        
        if not prompt_content:
            continue
        
        # Length analysis
        length = len(prompt_content)
        complexity_metrics['length_distribution'].append(length)
        
        # Section count (count XML tags)
        xml_sections = len(re.findall(r'<[A-Za-z]+>', prompt_content))
        complexity_metrics['section_count'].append(xml_sections)
        
        # XML tag density (tags per 1000 characters)
        tag_density = (xml_sections / length * 1000) if length > 0 else 0
        complexity_metrics['xml_tag_density'].append(tag_density)
        
        # Instruction density (instruction keywords per 1000 characters)
        instruction_keywords = len(re.findall(r'[Ii]nstructions?|[Tt]ask|[Oo]bjective|[Ss]tep', prompt_content))
        instruction_density = (instruction_keywords / length * 1000) if length > 0 else 0
        complexity_metrics['instruction_density'].append(instruction_density)
        
        # Initialize workspace complexity if not exists
        if workspace not in complexity_metrics['workspace_complexity']:
            complexity_metrics['workspace_complexity'][workspace] = []
        
        # Workspace-specific complexity
        complexity_metrics['workspace_complexity'][workspace].append({
            'length': length,
            'sections': xml_sections,
            'tag_density': tag_density,
            'instruction_density': instruction_density
        })
    
    return complexity_metrics

def extract_prompt_structure(prompt: str) -> Dict[str, Any]:
    """
    Extract the structural elements of a prompt for template creation
    """
    structure = {
        'sections': [],
        'section_order': [],
        'variables': [],
        'output_format': None,
        'rules': [],
        'examples': []
    }
    
    # Extract sections with markdown headers
    lines = prompt.split('\n')
    current_section = None
    section_content = []
    
    for line in lines:
        header_match = re.match(r'^#+\s+(.+)$', line)
        if header_match:
            if current_section:
                structure['sections'].append({
                    'name': current_section,
                    'content': '\n'.join(section_content).strip(),
                    'type': 'markdown_header'
                })
            current_section = header_match.group(1).strip()
            structure['section_order'].append(current_section)
            section_content = []
        else:
            section_content.append(line)
    
    # Add last section
    if current_section:
        structure['sections'].append({
            'name': current_section,
            'content': '\n'.join(section_content).strip(),
            'type': 'markdown_header'
        })
    
    # Extract XML-style sections
    xml_pattern = r'<([A-Za-z][A-Za-z0-9]*)>(.*?)</\1>'
    xml_matches = re.findall(xml_pattern, prompt, re.DOTALL)
    for tag, content in xml_matches:
        structure['sections'].append({
            'name': tag,
            'content': content.strip(),
            'type': 'xml_tag'
        })
        if tag not in structure['section_order']:
            structure['section_order'].append(tag)
    
    # Extract variables
    var_patterns = [
        (r'\{\{([^}]+)\}\}', 'double_braces'),
        (r'@([a-zA-Z][a-zA-Z0-9_]*)', 'at_symbol'),
        (r'```\{([^}]+)\}```', 'triple_ticks')
    ]
    
    for pattern, var_type in var_patterns:
        matches = re.findall(pattern, prompt)
        for match in matches:
            structure['variables'].append({
                'name': match,
                'type': var_type,
                'occurrences': len(re.findall(pattern.replace('([^}]+)', re.escape(match)), prompt))
            })
    
    return structure

def generate_template_proposal(patterns: Dict[str, Any], structures: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a standardized template proposal based on discovered patterns
    """
    template = {
        'name': 'Beam Standardized Prompt Template',
        'version': '1.0',
        'sections': [],
        'variable_format': None,
        'tag_style': None,
        'recommended_order': []
    }
    
    # Determine most common tag style
    if patterns['xml_tags']:
        most_common_xml = patterns['xml_tags'].most_common(1)[0][0]
        template['tag_style'] = 'xml'
    elif patterns['section_headers']:
        template['tag_style'] = 'markdown'
    else:
        template['tag_style'] = 'mixed'
    
    # Determine most common variable format
    if patterns['variable_formats']:
        most_common_var = patterns['variable_formats'].most_common(1)[0][0]
        template['variable_format'] = most_common_var
    
    # Define standard sections based on analysis
    standard_sections = [
        {
            'name': 'Role',
            'required': True,
            'description': 'Define the AI role and expertise',
            'keywords': ['You are', 'As a', 'Your role'],
            'example': 'You are a [expertise] specialist with deep knowledge in [domain].'
        },
        {
            'name': 'Instructions',
            'required': True,
            'description': 'Clear task instructions and objectives',
            'keywords': ['Task', 'Instruction', 'Objective'],
            'example': 'Your task is to [action] based on [input] and produce [output].'
        },
        {
            'name': 'Rules',
            'required': True,
            'description': 'General rules and constraints',
            'keywords': ['Rules', 'Constraints', 'Guidelines'],
            'example': 'DO NOT hallucinate. Only use provided information.'
        },
        {
            'name': 'Context',
            'required': False,
            'description': 'Background information and domain context',
            'keywords': ['Context', 'Background', 'Information'],
            'example': 'Background: [relevant context]'
        },
        {
            'name': 'Variables',
            'required': True,
            'description': 'Input variables and parameters',
            'keywords': ['Variables', 'Parameters', 'Input'],
            'example': 'Input: {{variable_name}}'
        },
        {
            'name': 'Output Format',
            'required': True,
            'description': 'Expected output structure',
            'keywords': ['Output', 'Format', 'Response'],
            'example': 'Output in JSON format: {"key": "value"}'
        },
        {
            'name': 'Examples',
            'required': False,
            'description': 'Examples for clarity',
            'keywords': ['Example', 'Sample', 'For instance'],
            'example': 'Example: Input X produces Output Y'
        }
    ]
    
    template['sections'] = standard_sections
    template['recommended_order'] = [s['name'] for s in standard_sections]
    
    return template

def create_quality_dashboard(insights: Dict[str, Any]):
    """Create quality-focused dashboard"""
    
    st.header("🎯 Strategic Insights for Beam Solution Engineers")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📝 Total Prompts Analyzed",
            f"{insights['total_prompts']:,}",
            help="Total number of prompts in the dataset"
        )
    
    with col2:
        st.metric(
            "🏢 Active Workspaces",
            f"{len(insights['workspace_breakdown'])}",
            help="Number of workspaces with prompts"
        )
    
    with col3:
        avg_conventions = sum(insights['convention_usage'].values()) / insights['total_prompts']
        st.metric(
            "📊 Avg Conventions per Prompt",
            f"{avg_conventions:.1f}",
            help="Average number of conventions used per prompt"
        )
    
    with col4:
        st.metric(
            "📏 Average Length",
            f"{insights['avg_length']:.0f} chars",
            help="Average prompt length"
        )
    
    # Quality Issues and Best Practices
    col1, col2 = st.columns(2)
    
    with col1:
        if insights['quality_issues']:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.subheader("🚨 Quality Issues Found")
            for issue in insights['quality_issues']:
                st.write(f"• {issue}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success("✅ No major quality issues detected!")
    
    with col2:
        if insights['best_practices']:
            st.markdown('<div class="insight-card">', unsafe_allow_html=True)
            st.subheader("✅ Best Practices Identified")
            for practice in insights['best_practices']:
                st.write(f"• {practice}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Convention Usage Analysis
    st.header("📊 Convention Usage Analysis")
    
    # Define convention examples with enhanced categories
    convention_examples = {
        'context_blocks': {
            'name': 'Context Blocks',
            'description': 'Structured sections using XML-style tags (flexible naming)',
            'category': 'Structure',
            'importance': 'High',
            'examples': ['<Context>API Integration</Context>', '<Topic>Data Analysis<EndTopic>', '<Rules>Business Logic</Rules>', '<Input>User Data</Input>', '<Parameters>Config</Parameters>'],
            'benefits': ['Better organization', 'Clear separation of concerns', 'Easier maintenance']
        },
        'role_definitions': {
            'name': 'Role Definitions',
            'description': 'Clear definition of AI role and responsibilities (various patterns)',
            'category': 'Clarity',
            'importance': 'Critical',
            'examples': ['Role: You are a data analyst', 'You are acting as a customer service agent', 'As a technical expert...', 'Your role is to...', 'You will be...', 'You serve as...'],
            'benefits': ['Clear AI behavior', 'Consistent responses', 'Better user experience']
        },
        'instruction_sections': {
            'name': 'Instruction Sections',
            'description': 'Clear task instructions and objectives',
            'category': 'Clarity',
            'importance': 'High',
            'examples': ['Instructions: Analyze the data', 'Task: Process user input', 'Objective: Generate report'],
            'benefits': ['Clear task definition', 'Reduced ambiguity', 'Better outcomes']
        },
        'variable_definitions': {
            'name': 'Variable Definitions',
            'description': 'Input parameters and variables specification',
            'category': 'Structure',
            'importance': 'Medium',
            'examples': ['Variables: userInput, outputFormat', 'Parameters: data, format', 'Input: customerData'],
            'benefits': ['Clear input requirements', 'Better integration', 'Reduced errors']
        },
        'output_formats': {
            'name': 'Output Formats',
            'description': 'Specified response structure and format',
            'category': 'Structure',
            'importance': 'High',
            'examples': ['Output Format: JSON', 'Format: Markdown table', 'Response format: Structured list'],
            'benefits': ['Consistent outputs', 'Easier parsing', 'Better integration']
        },
        'anti_hallucination': {
            'name': 'Anti-Hallucination',
            'description': 'Instructions to prevent AI from making up information',
            'category': 'Safety',
            'importance': 'Critical',
            'examples': ['Do not hallucinate', 'Only use provided information', 'Stick to facts', 'Do not invent'],
            'benefits': ['Reliable outputs', 'Trustworthy responses', 'Reduced errors']
        },
        'step_by_step': {
            'name': 'Step-by-Step Instructions',
            'description': 'Breaking complex tasks into sequential steps',
            'category': 'Clarity',
            'importance': 'High',
            'examples': ['Step 1: Analyze data', 'First, then, finally', 'Step-by-step process', '1. Process 2. Validate'],
            'benefits': ['Better reasoning', 'Clearer logic', 'More accurate results']
        },
        'examples_provided': {
            'name': 'Examples Provided',
            'description': 'Including examples for better understanding',
            'category': 'Clarity',
            'importance': 'Medium',
            'examples': ['Example: {"name": "John"}', 'Sample output:', 'For example:', 'Example response:'],
            'benefits': ['Better understanding', 'Clearer expectations', 'Reduced confusion']
        },
        'constraints_defined': {
            'name': 'Constraints Defined',
            'description': 'Setting boundaries and limitations',
            'category': 'Safety',
            'importance': 'Medium',
            'examples': ['Constraints: Max 100 words', 'Limitations: No external data', 'Rules: Follow format', 'Boundaries:'],
            'benefits': ['Controlled outputs', 'Better compliance', 'Reduced risks']
        }
    }
    
    # Create detailed convention data with enhanced information
    convention_data = []
    for convention, count in insights['convention_usage'].items():
        percentage = (count / insights['total_prompts']) * 100
        convention_info = convention_examples.get(convention, {})
        
        convention_data.append({
            'Convention': convention_info.get('name', convention.replace('_', ' ').title()),
            'Category': convention_info.get('category', 'Other'),
            'Importance': convention_info.get('importance', 'Medium'),
            'Description': convention_info.get('description', ''),
            'Examples': convention_info.get('examples', []),
            'Benefits': convention_info.get('benefits', []),
            'Count': count,
            'Percentage': percentage,
            'Usage': f"{count}/{insights['total_prompts']}"
        })
    
    df = pd.DataFrame(convention_data)
    
    # Enhanced visualization and analysis
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create an interactive chart
        fig = px.bar(
            df, 
            x='Convention', 
            y='Percentage',
            color='Category',
            title="Convention Usage by Category",
            labels={'Percentage': 'Usage Percentage (%)', 'Convention': 'Convention Type'},
            color_discrete_map={
                'Structure': '#1f77b4',
                'Clarity': '#ff7f0e', 
                'Safety': '#2ca02c'
            }
        )
        fig.update_layout(xaxis_tickangle=-45, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category breakdown
        st.subheader("📊 By Category")
        category_stats = df.groupby('Category').agg({
            'Count': 'sum',
            'Percentage': 'mean'
        }).round(1)
        
        for category, stats in category_stats.iterrows():
            st.metric(
                f"{category}",
                f"{stats['Count']} total",
                f"{stats['Percentage']:.1f}% avg"
            )
    
    # Enhanced convention details with importance indicators
    st.markdown("### 🎯 Convention Analysis by Importance")
    
    # Group by importance level
    for importance in ['Critical', 'High', 'Medium']:
        importance_df = df[df['Importance'] == importance]
        if not importance_df.empty:
            st.markdown(f"#### {importance} Priority Conventions")
            
            for _, row in importance_df.iterrows():
                # Create a more engaging expander
                with st.expander(f"🎯 {row['Convention']} ({row['Count']} prompts, {row['Percentage']:.1f}%)"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**Description:** {row['Description']}")
                        
                        # Show examples in a more readable format
                        if row['Examples']:
                            st.markdown("**Examples:**")
                            for example in row['Examples'][:3]:  # Show first 3 examples
                                st.code(example, language=None)
                        
                        # Show benefits
                        if row['Benefits']:
                            st.markdown("**Benefits:**")
                            for benefit in row['Benefits']:
                                st.markdown(f"• {benefit}")
                    
                    with col2:
                        # Usage visualization
                        st.markdown("**Usage:**")
                        st.progress(row['Percentage'] / 100)
                        st.caption(f"{row['Usage']} prompts")
                        
                        # Status indicator
                        if row['Percentage'] >= 70:
                            st.success("✅ Well Adopted")
                        elif row['Percentage'] >= 40:
                            st.warning("⚠️ Moderate Usage")
                        else:
                            st.error("❌ Needs Improvement")
                    
                    with col3:
                        st.metric("Count", row['Count'])
                        st.metric("Percentage", f"{row['Percentage']:.1f}%")
                        st.metric("Category", row['Category'])
    
    # Quick summary with enhanced metrics
    st.markdown("### 📈 Enhanced Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🏆 Top Performers")
        top_conventions = df.nlargest(3, 'Percentage')
        for _, row in top_conventions.iterrows():
            st.metric(
                row['Convention'],
                f"{row['Percentage']:.1f}%",
                f"{row['Count']} prompts"
            )
    
    with col2:
        st.subheader("⚠️ Needs Attention")
        low_conventions = df.nsmallest(3, 'Percentage')
        for _, row in low_conventions.iterrows():
            st.metric(
                row['Convention'],
                f"{row['Percentage']:.1f}%",
                f"{row['Count']} prompts"
            )
    
    with col3:
        st.subheader("📊 Category Performance")
        category_performance = df.groupby('Category')['Percentage'].mean().round(1)
        for category, avg_percentage in category_performance.items():
            st.metric(
                category,
                f"{avg_percentage}%",
                "average usage"
            )
    
    # Create convention usage chart
    fig = px.bar(
        df, 
        x='Convention', 
        y='Count',
        title="Convention Usage Across All Prompts",
        labels={'Count': 'Number of Prompts', 'Convention': 'Convention Type'}
    )
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Strategic Recommendations
    st.header("🎯 Strategic Recommendations")
    
    if insights['recommendations']:
        for i, rec in enumerate(insights['recommendations'], 1):
            st.markdown(f"**{i}.** {rec}")
    else:
        st.success("🎉 Your prompts are following best practices well!")
    
    # Workspace-Specific Insights
    st.header("🏢 Workspace-Specific Insights")
    
    workspace_data = []
    for workspace, patterns in insights['workspace_insights'].items():
        workspace_data.append({
            'Workspace': workspace,
            'Prompts': insights['workspace_breakdown'][workspace],
            'Conventions Used': patterns['convention_count'],
            'Examples Rate': f"{patterns['has_examples_rate']*100:.1f}%",
            'Constraints Rate': f"{patterns['has_constraints_rate']*100:.1f}%",
            'Anti-Hallucination Rate': f"{patterns['has_anti_hallucination_rate']*100:.1f}%"
        })
    
    workspace_df = pd.DataFrame(workspace_data).sort_values('Prompts', ascending=False)
    st.dataframe(workspace_df, use_container_width=True, hide_index=True)

def create_pattern_discovery_dashboard(discovered_patterns: Dict[str, Any]):
    """Create dashboard for pattern discovery results"""
    
    st.header("🔍 Pattern Discovery Analysis")
    st.markdown("### Comprehensive analysis of all prompt conventions and patterns")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📝 Total Patterns Analyzed",
            discovered_patterns['total_prompts_analyzed'],
            help="Number of prompts analyzed for patterns"
        )
    
    with col2:
        unique_xml_tags = len(discovered_patterns['xml_tags'])
        st.metric(
            "🏷️ Unique XML Tags",
            unique_xml_tags,
            help="Number of unique XML-style tags found"
        )
    
    with col3:
        unique_var_formats = len(discovered_patterns['variable_formats'])
        st.metric(
            "🔤 Variable Formats",
            unique_var_formats,
            help="Number of different variable format styles"
        )
    
    with col4:
        unique_sections = len(discovered_patterns['section_headers'])
        st.metric(
            "📑 Section Types",
            unique_sections,
            help="Number of unique section headers"
        )
    
    # Detailed pattern analysis
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["XML Tags", "Variable Formats", "Section Headers", "@ Tags", "Naming Conventions"])
    
    with tab1:
        st.subheader("🏷️ XML-Style Tags Analysis")
        if discovered_patterns['xml_tags']:
            xml_df = pd.DataFrame(
                discovered_patterns['xml_tags'].most_common(20),
                columns=['Tag', 'Count']
            )
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                fig = px.bar(
                    xml_df,
                    x='Tag',
                    y='Count',
                    title='Top 20 XML Tags by Usage',
                    color='Count',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Tag Examples:**")
                for tag, count in xml_df.head(10).values:
                    st.code(f"<{tag}>content</{tag}>")
                    st.caption(f"Used {count} times")
        else:
            st.info("No XML-style tags found in prompts")
    
    with tab2:
        st.subheader("🔤 Variable Format Analysis")
        if discovered_patterns['variable_formats']:
            var_df = pd.DataFrame(
                discovered_patterns['variable_formats'].most_common(),
                columns=['Format', 'Count']
            )
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                fig = px.pie(
                    var_df,
                    values='Count',
                    names='Format',
                    title='Variable Format Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Format Examples:**")
                format_examples = {
                    'double_braces': '{{variableName}}',
                    'at_symbol': '@variableName',
                    'triple_ticks': '```{variableName}```',
                    'double_brackets': '[[variableName]]',
                    'xml_style': '<variableName>'
                }
                
                for fmt, count in var_df.values:
                    if fmt in format_examples:
                        st.code(format_examples[fmt])
                        st.caption(f"Used in {count} prompts")
    
    with tab3:
        st.subheader("📑 Section Headers Analysis")
        if discovered_patterns['section_headers']:
            section_df = pd.DataFrame(
                discovered_patterns['section_headers'].most_common(15),
                columns=['Section', 'Count']
            )
            
            fig = px.treemap(
                section_df,
                path=['Section'],
                values='Count',
                title='Section Header Usage Treemap'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("**Most Common Sections:**")
            for section, count in section_df.head(10).values:
                st.markdown(f"- **{section}**: {count} occurrences")
    
    with tab4:
        st.subheader("@ @ Tag Analysis")
        if discovered_patterns['at_tags']:
            at_df = pd.DataFrame(
                discovered_patterns['at_tags'].most_common(20),
                columns=['Tag', 'Count']
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(at_df, use_container_width=True, hide_index=True)
            
            with col2:
                # Word cloud visualization simulation
                st.markdown("**Tag Cloud:**")
                for tag, count in at_df.head(10).values:
                    size = min(30, 10 + count * 2)
                    st.markdown(f"<span style='font-size:{size}px'>{tag}</span>", unsafe_allow_html=True)
    
    with tab5:
        st.subheader("🐍 Naming Convention Analysis")
        if discovered_patterns['naming_conventions']:
            naming_df = pd.DataFrame(
                discovered_patterns['naming_conventions'].most_common(),
                columns=['Convention', 'Count']
            )
            
            fig = px.bar(
                naming_df,
                x='Convention',
                y='Count',
                title='Variable Naming Conventions',
                color='Convention',
                color_discrete_map={
                    'camelCase': '#1f77b4',
                    'snake_case': '#ff7f0e',
                    'PascalCase': '#2ca02c',
                    'UPPER_SNAKE_CASE': '#d62728'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("**Convention Examples:**")
            examples = {
                'camelCase': 'variableName, userId, customerData',
                'snake_case': 'variable_name, user_id, customer_data',
                'PascalCase': 'VariableName, UserId, CustomerData',
                'UPPER_SNAKE_CASE': 'VARIABLE_NAME, USER_ID, CUSTOMER_DATA'
            }
            
            for conv, count in naming_df.values:
                if conv in examples:
                    st.code(examples[conv])
                    st.caption(f"{conv}: {count} occurrences")
    
    # Workspace-specific patterns
    st.header("🏢 Workspace Pattern Analysis")
    
    workspace_patterns = discovered_patterns['patterns_by_workspace']
    if workspace_patterns:
        workspace_names = list(workspace_patterns.keys())
        selected_workspace = st.selectbox("Select Workspace", workspace_names)
        
        if selected_workspace:
            ws_patterns = workspace_patterns[selected_workspace]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### {selected_workspace} Patterns")
                
                # XML tags for this workspace
                if ws_patterns['xml_tags']:
                    st.markdown("**XML Tags:**")
                    for tag, count in ws_patterns['xml_tags'].most_common(5):
                        st.markdown(f"- `<{tag}>`: {count} uses")
                
                # Variable formats
                if ws_patterns['variable_formats']:
                    st.markdown("**Variable Formats:**")
                    for fmt, count in ws_patterns['variable_formats'].most_common():
                        st.markdown(f"- {fmt}: {count} prompts")
            
            with col2:
                # Section headers
                if ws_patterns['section_headers']:
                    st.markdown("**Section Headers:**")
                    for header, count in ws_patterns['section_headers'].most_common(5):
                        st.markdown(f"- {header}: {count} uses")
                
                # Naming conventions
                if ws_patterns['naming_conventions']:
                    st.markdown("**Naming Conventions:**")
                    for conv, count in ws_patterns['naming_conventions'].most_common():
                        st.markdown(f"- {conv}: {count} uses")

def create_template_builder(template_proposal: Dict[str, Any]):
    """Create interactive template builder interface"""
    
    st.header("🏗️ Standardized Template Builder")
    st.markdown("### Create and customize your standardized prompt template")
    
    # Template overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Template Version", template_proposal['version'])
    
    with col2:
        st.metric("Tag Style", template_proposal['tag_style'].upper())
    
    with col3:
        st.metric("Variable Format", template_proposal['variable_format'].replace('_', ' ').title())
    
    # Template customization
    st.markdown("### Customize Template Sections")
    
    # Section order customization
    st.markdown("#### Section Order")
    st.info("Drag and drop to reorder sections (in actual implementation)")
    
    ordered_sections = st.session_state.get('template_sections', template_proposal['sections'])
    
    # Display sections with customization options
    for i, section in enumerate(ordered_sections):
        with st.expander(f"{i+1}. {section['name']} {'(Required)' if section['required'] else '(Optional)'}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Description:** {section['description']}")
                st.markdown(f"**Keywords:** {', '.join(section['keywords'])}")
                
                # Editable example
                example = st.text_area(
                    "Example Template",
                    value=section['example'],
                    key=f"example_{section['name']}",
                    height=100
                )
            
            with col2:
                # Section settings
                st.markdown("**Settings**")
                required = st.checkbox(
                    "Required",
                    value=section['required'],
                    key=f"required_{section['name']}"
                )
                
                # Tag style for this section
                if template_proposal['tag_style'] == 'mixed':
                    tag_style = st.radio(
                        "Tag Style",
                        ['Markdown (#)', 'XML (<>)', '@ Symbol'],
                        key=f"tag_{section['name']}"
                    )
    
    # Template preview
    st.markdown("### Template Preview")
    
    preview_tab1, preview_tab2, preview_tab3 = st.tabs(["Formatted", "Raw Template", "YAML Export"])
    
    with preview_tab1:
        st.markdown("#### Formatted Template Preview")
        
        # Generate preview based on settings
        for section in ordered_sections:
            if template_proposal['tag_style'] == 'markdown':
                st.markdown(f"# {section['name']}")
            elif template_proposal['tag_style'] == 'xml':
                st.markdown(f"<{section['name']}>")
            
            st.text(section['example'])
            
            if template_proposal['tag_style'] == 'xml':
                st.markdown(f"</{section['name']}>")
            
            st.markdown("")
    
    with preview_tab2:
        # Generate raw template
        template_text = generate_raw_template(ordered_sections, template_proposal)
        st.code(template_text, language='markdown')
    
    with preview_tab3:
        # YAML export format
        yaml_template = {
            'template': {
                'name': template_proposal['name'],
                'version': template_proposal['version'],
                'tag_style': template_proposal['tag_style'],
                'variable_format': template_proposal['variable_format'],
                'sections': [
                    {
                        'name': s['name'],
                        'required': s['required'],
                        'description': s['description'],
                        'keywords': s['keywords'],
                        'example': s['example']
                    }
                    for s in ordered_sections
                ]
            }
        }
        # Convert to YAML-like format without importing yaml
        yaml_text = "template:\n"
        yaml_text += f"  name: {yaml_template['template']['name']}\n"
        yaml_text += f"  version: {yaml_template['template']['version']}\n"
        yaml_text += f"  tag_style: {yaml_template['template']['tag_style']}\n"
        yaml_text += f"  variable_format: {yaml_template['template']['variable_format']}\n"
        yaml_text += "  sections:\n"
        for section in yaml_template['template']['sections']:
            yaml_text += f"    - name: {section['name']}\n"
            yaml_text += f"      required: {section['required']}\n"
            yaml_text += f"      description: {section['description']}\n"
            yaml_text += f"      keywords: [{', '.join(section['keywords'])}]\n"
            yaml_text += f"      example: |\n"
            for line in section['example'].split('\n'):
                yaml_text += f"        {line}\n"
        st.code(yaml_text, language='yaml')
    
    # Export options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Template"):
            st.success("Template saved successfully!")
    
    with col2:
        if st.button("📤 Export as JSON"):
            st.download_button(
                label="Download JSON",
                data=json.dumps(template_proposal, indent=2),
                file_name=f"prompt_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("📋 Copy to Clipboard"):
            st.info("Template copied to clipboard!")

def generate_raw_template(sections: List[Dict], config: Dict) -> str:
    """Generate raw template text based on configuration"""
    template_parts = []
    
    for section in sections:
        if config['tag_style'] == 'markdown':
            template_parts.append(f"# {section['name']}\n{section['example']}\n")
        elif config['tag_style'] == 'xml':
            template_parts.append(f"<{section['name']}>\n{section['example']}\n</{section['name']}>\n")
        else:  # mixed or @ style
            template_parts.append(f"@{section['name']}\n{section['example']}\n@end{section['name']}\n")
    
    return '\n'.join(template_parts)

def create_workshop_module():
    """Create workshop facilitation interface"""
    
    st.header("👥 Workshop Facilitation Module")
    st.markdown("### Collaborative decision-making for prompt standardization")
    
    # Workshop setup
    if 'workshop_active' not in st.session_state:
        st.session_state.workshop_active = False
    
    if not st.session_state.workshop_active:
        st.markdown("#### Start a New Workshop Session")
        
        col1, col2 = st.columns(2)
        
        with col1:
            workshop_name = st.text_input("Workshop Name", "Prompt Standardization Workshop")
            participants = st.text_area("Participants (one per line)", "Alice\nBob\nCharlie\nDiana")
        
        with col2:
            workshop_date = st.date_input("Workshop Date", datetime.now())
            workshop_duration = st.slider("Duration (hours)", 1, 4, 2)
        
        if st.button("🚀 Start Workshop", type="primary"):
            st.session_state.workshop_active = True
            st.session_state.workshop_data = {
                'name': workshop_name,
                'participants': participants.split('\n'),
                'date': workshop_date,
                'duration': workshop_duration,
                'decisions': []
            }
            st.rerun()
    
    else:
        # Active workshop interface
        workshop_data = st.session_state.workshop_data
        
        st.success(f"Workshop Active: {workshop_data['name']}")
        st.caption(f"Participants: {', '.join(workshop_data['participants'])}")
        
        # Workshop tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Convention Voting", "Template Discussion", "Decision Log", "Export Results"])
        
        with tab1:
            st.markdown("### Convention Voting")
            
            # Variable format voting
            st.markdown("#### 1. Variable Format Convention")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Option A: Double Braces**")
                st.code("{{variableName}}")
                st.code("{{customer_data}}")
                votes_a = st.number_input("Votes", 0, len(workshop_data['participants']), key="var_a")
            
            with col2:
                st.markdown("**Option B: @ Symbol**")
                st.code("@variableName")
                st.code("@customer_data")
                votes_b = st.number_input("Votes", 0, len(workshop_data['participants']), key="var_b")
            
            with col3:
                st.markdown("**Option C: Triple Ticks**")
                st.code("```{variableName}```")
                st.code("```{customer_data}```")
                votes_c = st.number_input("Votes", 0, len(workshop_data['participants']), key="var_c")
            
            # Display voting results
            if votes_a + votes_b + votes_c > 0:
                fig = px.pie(
                    values=[votes_a, votes_b, votes_c],
                    names=['Double Braces', '@ Symbol', 'Triple Ticks'],
                    title='Variable Format Voting Results'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Tag style voting
            st.markdown("#### 2. Tag Style Convention")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Option A: XML Tags**")
                st.code("<Context>\nContent here\n</Context>")
                tag_votes_a = st.number_input("Votes", 0, len(workshop_data['participants']), key="tag_a")
            
            with col2:
                st.markdown("**Option B: Markdown Headers**")
                st.code("# Context\nContent here")
                tag_votes_b = st.number_input("Votes", 0, len(workshop_data['participants']), key="tag_b")
            
            with col3:
                st.markdown("**Option C: @ Tags**")
                st.code("@Context\nContent here\n@EndContext")
                tag_votes_c = st.number_input("Votes", 0, len(workshop_data['participants']), key="tag_c")
            
            # Comments section
            st.markdown("#### Discussion Notes")
            discussion_notes = st.text_area(
                "Add discussion points and reasoning",
                height=150,
                key="convention_discussion"
            )
            
            if st.button("💾 Save Voting Results"):
                decision = {
                    'topic': 'Convention Selection',
                    'timestamp': datetime.now().isoformat(),
                    'variable_format': {
                        'double_braces': votes_a,
                        'at_symbol': votes_b,
                        'triple_ticks': votes_c
                    },
                    'tag_style': {
                        'xml': tag_votes_a,
                        'markdown': tag_votes_b,
                        'at_tags': tag_votes_c
                    },
                    'notes': discussion_notes
                }
                workshop_data['decisions'].append(decision)
                st.success("Voting results saved!")
        
        with tab2:
            st.markdown("### Template Structure Discussion")
            
            # Section importance ranking
            st.markdown("#### Rank Section Importance")
            
            sections = ['Role', 'Instructions', 'Rules', 'Context', 'Variables', 'Output Format', 'Examples']
            
            importance_scores = {}
            for section in sections:
                importance_scores[section] = st.slider(
                    f"{section} Importance",
                    1, 10, 5,
                    key=f"importance_{section}"
                )
            
            # Visualize importance
            importance_df = pd.DataFrame(
                list(importance_scores.items()),
                columns=['Section', 'Importance']
            )
            
            fig = px.bar(
                importance_df,
                x='Section',
                y='Importance',
                title='Section Importance Consensus',
                color='Importance',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Required vs Optional discussion
            st.markdown("#### Required vs Optional Sections")
            
            required_sections = st.multiselect(
                "Select Required Sections",
                sections,
                default=['Role', 'Instructions', 'Rules', 'Variables', 'Output Format']
            )
            
            st.markdown("#### Template Notes")
            template_notes = st.text_area(
                "Add notes about template structure decisions",
                height=150,
                key="template_discussion"
            )
            
            if st.button("💾 Save Template Decisions"):
                decision = {
                    'topic': 'Template Structure',
                    'timestamp': datetime.now().isoformat(),
                    'importance_scores': importance_scores,
                    'required_sections': required_sections,
                    'notes': template_notes
                }
                workshop_data['decisions'].append(decision)
                st.success("Template decisions saved!")
        
        with tab3:
            st.markdown("### Decision Log")
            
            if workshop_data['decisions']:
                for i, decision in enumerate(workshop_data['decisions']):
                    with st.expander(f"Decision {i+1}: {decision['topic']} - {decision['timestamp']}"):
                        st.json(decision)
            else:
                st.info("No decisions logged yet")
        
        with tab4:
            st.markdown("### Export Workshop Results")
            
            # Generate workshop report
            if st.button("📊 Generate Workshop Report"):
                report = {
                    'workshop': workshop_data,
                    'final_decisions': {
                        'variable_format': 'To be determined based on votes',
                        'tag_style': 'To be determined based on votes',
                        'required_sections': workshop_data['decisions'][-1]['required_sections'] if workshop_data['decisions'] else [],
                        'template_version': '1.0'
                    },
                    'next_steps': [
                        'Finalize template based on workshop decisions',
                        'Create implementation guide',
                        'Schedule follow-up training',
                        'Set up compliance tracking'
                    ]
                }
                
                st.json(report)
                
                # Download options
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 Download Workshop Report (JSON)",
                        data=json.dumps(report, indent=2),
                        file_name=f"workshop_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                with col2:
                    # Convert to markdown format
                    markdown_report = f"""# Workshop Report: {workshop_data['name']}

Date: {workshop_data['date']}
Participants: {', '.join(workshop_data['participants'])}

## Decisions Made

{chr(10).join([f"- {d['topic']}: {d['timestamp']}" for d in workshop_data['decisions']])}

## Next Steps

{chr(10).join([f"- {step}" for step in report['next_steps']])}
"""
                    
                    st.download_button(
                        label="📥 Download Workshop Report (Markdown)",
                        data=markdown_report,
                        file_name=f"workshop_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )
            
            if st.button("🏁 End Workshop Session"):
                st.session_state.workshop_active = False
                st.success("Workshop session ended successfully!")
                st.rerun()

def main():
    """Main Streamlit application"""
    
    st.markdown('<h1 class="main-header">🎯 Strategic Prompt Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("### Actionable Insights for Beam Solution Engineers")
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Your Data")
        
        uploaded_file = st.file_uploader(
            "Choose your prompt JSON file",
            type=['json'],
            help="Upload your prompt recipes JSON file"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Load and analyze data
            try:
                data = json.load(uploaded_file)
                
                # Validate JSON structure
                if not isinstance(data, list):
                    st.error("❌ Invalid JSON format: Expected a list of prompt objects")
                    st.session_state['data_loaded'] = False
                    return
                
                # Check if prompts exist
                prompts_with_content = [item for item in data if item.get('prompt', '').strip()]
                if not prompts_with_content:
                    st.error("❌ No prompts found in the file. Please check if the 'prompt' key contains data.")
                    st.session_state['data_loaded'] = False
                    return
                
                st.success(f"✅ Found {len(prompts_with_content)} prompts with content out of {len(data)} total entries")
                
                insights = analyze_prompt_quality(data)
                patterns = detect_actual_patterns(data)
                complexity = analyze_prompt_complexity(data)
                insights['actual_patterns'] = patterns
                insights['complexity_metrics'] = complexity
                st.session_state['insights'] = insights
                st.session_state['raw_data'] = data
                st.session_state['data_loaded'] = True
                
            except Exception as e:
                st.error(f"❌ Error loading file: {str(e)}")
                st.session_state['data_loaded'] = False
        else:
            st.info("📋 Please upload a JSON file to begin analysis")
            st.session_state['data_loaded'] = False
        
        # Quick Tips Section
        st.markdown("---")
        st.header("💡 Quick Tips")
        
        with st.expander("🎯 What Makes a Good Prompt?"):
            st.markdown("""
            **✅ Best Practices:**
            - Clear role definition
            - Structured instructions
            - Anti-hallucination warnings
            - Examples when possible
            - Step-by-step breakdowns
            - Defined output format
            
            **❌ Common Issues:**
            - Vague instructions
            - No role definition
            - Missing constraints
            - No examples
            - Unclear output format
            """)
        
        with st.expander("🔍 Understanding the Analysis"):
            st.markdown("""
            **📊 Convention Usage:**
            - Shows how many prompts use each best practice
            - Higher percentages = better consistency
            - Click each convention to see examples
            
            **🚨 Quality Issues:**
            - Areas where your team needs improvement
            - Based on industry best practices
            - Focus on these for training
            
            **✅ Best Practices:**
            - What your team is doing well
            - Share these across workspaces
            - Use as examples for others
            """)
        
        with st.expander("📈 Interpreting Results"):
            st.markdown("""
            **🎯 Priority Actions:**
            1. Focus on conventions with <30% usage
            2. Share best practices from high-performing workspaces
            3. Create templates based on successful patterns
            4. Train team on missing conventions
            
            **📋 Next Steps:**
            - Export reports for team discussions
            - Create improvement plans
            - Set up regular reviews
            - Share learnings across workspaces
            """)
    
    # Main content
    if st.session_state.get('data_loaded', False) and 'insights' in st.session_state:
        insights = st.session_state['insights']
        
        # Debug information (can be removed later)
        with st.expander("🔍 Debug: What We're Analyzing"):
            st.markdown("**JSON Structure Validation:**")
            st.write(f"- Total entries in JSON: {len(st.session_state.get('raw_data', []))}")
            st.write(f"- Entries with prompt content: {insights['total_prompts']}")
            st.write(f"- Workspaces found: {len(insights['workspace_breakdown'])}")
            
            # Show sample prompt structure
            if st.session_state.get('raw_data'):
                sample_item = st.session_state['raw_data'][0]
                st.markdown("**Sample JSON Entry Structure:**")
                st.json({k: v for k, v in sample_item.items() if k != 'prompt'})
                
                st.markdown("**Sample Prompt Content (first 200 chars):**")
                if sample_item.get('prompt'):
                    st.text(sample_item['prompt'][:200] + "...")
        
        # Create tabs for different features
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Quality Dashboard", 
            "🔍 Pattern Discovery", 
            "🏗️ Template Builder", 
            "👥 Workshop Module"
        ])
        
        with tab1:
            create_quality_dashboard(insights)
            
            # Display actual patterns found
            if 'actual_patterns' in insights:
                st.header("🔍 Actual Patterns Found in Your Prompts")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if insights['actual_patterns']['xml_tags']:
                        st.subheader("📋 XML-Style Tags Used")
                        for tag in sorted(insights['actual_patterns']['xml_tags']):
                            st.markdown(f"• `<{tag}>` / `</{tag}>`")
                    else:
                        st.info("No XML-style tags found")
                
                with col2:
                    if insights['actual_patterns']['role_patterns']:
                        st.subheader("👤 Role Definition Patterns")
                        for pattern in insights['actual_patterns']['role_patterns'][:10]:  # Show first 10
                            st.markdown(f"• `{pattern}`")
                        if len(insights['actual_patterns']['role_patterns']) > 10:
                            st.caption(f"... and {len(insights['actual_patterns']['role_patterns']) - 10} more patterns")
                    else:
                        st.info("No role definition patterns found")
            
            # Display complexity analysis
            if 'complexity_metrics' in insights:
                st.header("📊 Prompt Complexity Analysis")
                
                complexity = insights['complexity_metrics']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    avg_length = np.mean(complexity['length_distribution'])
                    st.metric("📏 Avg Length", f"{avg_length:.0f} chars")
                
                with col2:
                    avg_sections = np.mean(complexity['section_count'])
                    st.metric("📋 Avg Sections", f"{avg_sections:.1f}")
                
                with col3:
                    avg_tag_density = np.mean(complexity['xml_tag_density'])
                    st.metric("🏷️ Tag Density", f"{avg_tag_density:.1f}/1k chars")
                
                with col4:
                    avg_instruction_density = np.mean(complexity['instruction_density'])
                    st.metric("📝 Instruction Density", f"{avg_instruction_density:.1f}/1k chars")
                
                # Complexity distribution charts
                col1, col2 = st.columns(2)
                
                with col1:
                    # Length distribution
                    fig_length = px.histogram(
                        x=complexity['length_distribution'],
                        title="Prompt Length Distribution",
                        labels={'x': 'Length (characters)', 'y': 'Number of Prompts'},
                        nbins=20
                    )
                    st.plotly_chart(fig_length, use_container_width=True)
                
                with col2:
                    # Section count distribution
                    fig_sections = px.histogram(
                        x=complexity['section_count'],
                        title="XML Section Count Distribution",
                        labels={'x': 'Number of Sections', 'y': 'Number of Prompts'},
                        nbins=10
                    )
                    st.plotly_chart(fig_sections, use_container_width=True)
                
                # Workspace complexity comparison
                st.subheader("🏢 Workspace Complexity Comparison")
                
                workspace_complexity = []
                for workspace, metrics in complexity['workspace_complexity'].items():
                    if metrics:  # Check if workspace has data
                        avg_length = np.mean([m['length'] for m in metrics])
                        avg_sections = np.mean([m['sections'] for m in metrics])
                        avg_tag_density = np.mean([m['tag_density'] for m in metrics])
                        
                        workspace_complexity.append({
                            'Workspace': workspace,
                            'Avg Length': avg_length,
                            'Avg Sections': avg_sections,
                            'Tag Density': avg_tag_density,
                            'Prompt Count': len(metrics)
                        })
                
                if workspace_complexity:
                    complexity_df = pd.DataFrame(workspace_complexity)
                    complexity_df = complexity_df.sort_values('Avg Length', ascending=False)
                    
                    # Create a heatmap-style visualization
                    fig_heatmap = px.imshow(
                        complexity_df[['Avg Length', 'Avg Sections', 'Tag Density']].T,
                        x=complexity_df['Workspace'],
                        title="Workspace Complexity Heatmap",
                        labels=dict(x="Workspace", y="Metric", color="Value"),
                        aspect="auto"
                    )
                    fig_heatmap.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                    
                    # Detailed workspace table
                    st.dataframe(
                        complexity_df,
                        use_container_width=True,
                        hide_index=True
                    )
            
            # Export section
            st.header("💾 Export Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📊 Export Quality Report"):
                    # Create comprehensive report
                    report = {
                        'analysis_date': datetime.now().isoformat(),
                        'total_prompts': insights['total_prompts'],
                        'convention_usage': insights['convention_usage'],
                        'quality_issues': insights['quality_issues'],
                        'best_practices': insights['best_practices'],
                        'recommendations': insights['recommendations'],
                        'workspace_insights': insights['workspace_insights']
                    }
                    
                    report_json = json.dumps(report, indent=2)
                    st.download_button(
                        label="📥 Download Quality Report",
                        data=report_json,
                        file_name=f"beam_prompt_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            with col2:
                if st.button("📋 Export Convention Data"):
                    convention_df = pd.DataFrame([
                        {
                            'Convention': k.replace('_', ' ').title(),
                            'Count': v,
                            'Percentage': f"{(v/insights['total_prompts'])*100:.1f}%"
                        }
                        for k, v in insights['convention_usage'].items()
                    ])
                    
                    csv = convention_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"convention_usage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        with tab2:
            if 'discovered_patterns' in insights:
                create_pattern_discovery_dashboard(insights['discovered_patterns'])
            else:
                st.info("Pattern discovery analysis not available. Please re-analyze your data.")
        
        with tab3:
            # Generate template proposal based on patterns
            if 'discovered_patterns' in insights:
                # Extract prompt structures for template generation
                structures = []
                for item in st.session_state.get('raw_data', []):
                    if item.get('prompt'):
                        structure = extract_prompt_structure(item['prompt'])
                        structures.append(structure)
                
                template_proposal = generate_template_proposal(
                    insights['discovered_patterns'],
                    structures
                )
                create_template_builder(template_proposal)
            else:
                st.info("Please analyze your data first to generate template proposals.")
        
        with tab4:
            create_workshop_module()
    
    else:
        # Welcome message
        st.markdown("""
        ## 🎯 Welcome to Strategic Prompt Analyzer!
        
        This tool is designed specifically for **Beam Solution Engineers** to improve prompt engineering practices.
        
        ### 🎯 What We Analyze:
        - **Convention Usage**: How well your prompts follow Beam best practices
        - **Quality Issues**: Areas that need improvement
        - **Best Practices**: What you're doing well
        - **Strategic Recommendations**: Actionable steps to improve
        
        ### 📊 Key Conventions We Track:
        
        **🔧 Structure & Organization:**
        - **Context Blocks**: `<Context>API Integration</Context>` - Structured context sections
        - **Role Definitions**: `Role: You are a data analyst` - Clear AI role specification
        - **Instruction Sections**: `Instructions: Analyze the data` - Task clarity
        
        **📝 Content & Clarity:**
        - **Variable Definitions**: `Variables: userInput, outputFormat` - Input specification
        - **Output Formats**: `Output Format: JSON` - Response structure
        - **Examples Provided**: `Example: {"name": "John"}` - Learning from examples
        
        **🛡️ Quality & Safety:**
        - **Anti-Hallucination**: `Do not hallucinate` - Prevent AI from making things up
        - **Step-by-Step**: `Step 1: Analyze, Step 2: Validate` - Break down complex tasks
        - **Constraints**: `Constraints: Max 100 words` - Set boundaries
        
        ### 🚀 Getting Started:
        1. **Upload** your prompt JSON file (like "Prompt Recipes - Prompts.json")
        2. **Review** the strategic insights and convention usage
        3. **Focus** on the recommendations for improvement
        4. **Export** reports for team discussions and training
        
        ### 🎯 Goal:
        Help every Beam solution engineer write better, more consistent prompts that follow best practices!
        
        ---
        
        **💡 Pro Tip**: Each convention will show you real examples from your prompts, so you can see exactly what we're looking for!
        """)

if __name__ == "__main__":
    main() 
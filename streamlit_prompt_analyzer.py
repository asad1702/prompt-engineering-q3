#!/usr/bin/env python3
"""
Streamlit Prompt Analyzer
Modern web-based interface for workspace and prompt analysis
"""

import streamlit as st
import json
import pandas as pd
import re
from collections import Counter
from typing import Dict, List, Any, Tuple
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="🏢 Prompt Analyzer",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .query-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    .result-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_analyze_json(uploaded_file) -> Dict[str, Any]:
    """
    Load and analyze JSON file with caching for performance
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Load JSON data
        data = json.load(uploaded_file)
        
        # Initialize counters and storage
        workspace_counts = Counter()
        workspace_details = {}
        all_agents = set()
        all_tools = set()
        all_prompt_lengths = []
        
        # Process each prompt
        for item in data:
            workspace_name = item.get('workspace_name', 'Unknown Workspace')
            agent_name = item.get('agent_name', 'Unknown Agent')
            tool_name = item.get('tool_name', 'Unknown Tool')
            prompt_content = item.get('prompt', '')
            
            # Count workspace occurrences
            workspace_counts[workspace_name] += 1
            
            # Collect unique agents and tools
            all_agents.add(agent_name)
            all_tools.add(tool_name)
            
            # Store prompt length
            all_prompt_lengths.append(len(prompt_content))
            
            # Store details for each workspace
            if workspace_name not in workspace_details:
                workspace_details[workspace_name] = {
                    'total_prompts': 0,
                    'agents': set(),
                    'tools': set(),
                    'prompts': [],
                    'total_chars': 0
                }
            
            workspace_details[workspace_name]['total_prompts'] += 1
            workspace_details[workspace_name]['agents'].add(agent_name)
            workspace_details[workspace_name]['tools'].add(tool_name)
            workspace_details[workspace_name]['total_chars'] += len(prompt_content)
            
            # Store prompt info
            prompt_info = {
                'agent_name': agent_name,
                'tool_name': tool_name,
                'tool_category': item.get('tool_category', 'Unknown'),
                'prompt_length': len(prompt_content),
                'prompt_content': prompt_content,
                'workspace_name': workspace_name
            }
            workspace_details[workspace_name]['prompts'].append(prompt_info)
        
        # Convert sets to lists for JSON serialization
        for workspace_name in workspace_details:
            workspace_details[workspace_name]['agents'] = list(workspace_details[workspace_name]['agents'])
            workspace_details[workspace_name]['tools'] = list(workspace_details[workspace_name]['tools'])
        
        # Calculate prompt length statistics
        prompt_stats = {
            'avg_length': sum(all_prompt_lengths) / len(all_prompt_lengths) if all_prompt_lengths else 0,
            'min_length': min(all_prompt_lengths) if all_prompt_lengths else 0,
            'max_length': max(all_prompt_lengths) if all_prompt_lengths else 0,
            'total_chars': sum(all_prompt_lengths),
            'total_prompts': len(all_prompt_lengths)
        }
        
        # Count prompt conventions
        convention_counts = count_prompt_conventions(data)
        
        return {
            'total_prompts': len(data),
            'total_workspaces': len(workspace_counts),
            'total_agents': len(all_agents),
            'total_tools': len(all_tools),
            'workspace_counts': dict(workspace_counts),
            'workspace_details': workspace_details,
            'prompt_stats': prompt_stats,
            'all_prompt_lengths': all_prompt_lengths,
            'convention_counts': convention_counts,
            'raw_data': data  # Store raw data for querying
        }
        
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def search_prompts_for_pattern(analysis_data: Dict[str, Any], query: str) -> Tuple[int, List[Dict]]:
    """
    Search through all prompts for a specific pattern
    
    Args:
        analysis_data: Analysis results dictionary
        query: Search query/pattern
        
    Returns:
        Tuple of (count, list of matching prompts)
    """
    if not analysis_data or 'raw_data' not in analysis_data:
        return 0, []
    
    matching_prompts = []
    count = 0
    
    for item in analysis_data['raw_data']:
        prompt_content = item.get('prompt', '')
        
        # Try different search strategies
        if query.lower() in prompt_content.lower():
            count += 1
            matching_prompts.append({
                'workspace': item.get('workspace_name', 'Unknown'),
                'agent': item.get('agent_name', 'Unknown'),
                'tool': item.get('tool_name', 'Unknown'),
                'length': len(prompt_content),
                'content_preview': prompt_content[:200] + '...' if len(prompt_content) > 200 else prompt_content
            })
    
    return count, matching_prompts

def search_prompts_with_regex(analysis_data: Dict[str, Any], pattern: str) -> Tuple[int, List[Dict]]:
    """
    Search through all prompts using regex patterns
    
    Args:
        analysis_data: Analysis results dictionary
        pattern: Regex pattern to search for
        
    Returns:
        Tuple of (count, list of matching prompts)
    """
    if not analysis_data or 'raw_data' not in analysis_data:
        return 0, []
    
    matching_prompts = []
    count = 0
    
    try:
        regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        
        for item in analysis_data['raw_data']:
            prompt_content = item.get('prompt', '')
            
            if regex.search(prompt_content):
                count += 1
                matching_prompts.append({
                    'workspace': item.get('workspace_name', 'Unknown'),
                    'agent': item.get('agent_name', 'Unknown'),
                    'tool': item.get('tool_name', 'Unknown'),
                    'length': len(prompt_content),
                    'content_preview': prompt_content[:200] + '...' if len(prompt_content) > 200 else prompt_content
                })
    
    except re.error as e:
        st.error(f"Invalid regex pattern: {str(e)}")
        return 0, []
    
    return count, matching_prompts

def count_prompt_conventions(data: List[Dict]) -> Dict[str, int]:
    """
    Count prompt conventions used across all prompts
    
    Args:
        data: List of prompt dictionaries from JSON
        
    Returns:
        Dictionary with convention names as keys and counts as values
    """
    conventions = {
        '@topic and @endTopic': 0,
        '<topic> and </topic>': 0,
        '<Context> and <EndContext>': 0,
        '<Parameter>': 0,
        'camelCase variables': 0,
        'snake_case variables': 0
    }
    
    for item in data:
        prompt_content = item.get('prompt', '')
        if not prompt_content:
            continue
        
        # Check for @topic and @endTopic (both must be present)
        if '@topic' in prompt_content and '@endTopic' in prompt_content:
            conventions['@topic and @endTopic'] += 1
        
        # Check for <topic> and </topic> (both must be present)
        if '<topic>' in prompt_content and '</topic>' in prompt_content:
            conventions['<topic> and </topic>'] += 1
        
        # Check for <Context> and <EndContext> (both must be present)
        if '<Context>' in prompt_content and '<EndContext>' in prompt_content:
            conventions['<Context> and <EndContext>'] += 1
        
        # Check for <Parameter> (can appear standalone)
        if '<Parameter>' in prompt_content:
            conventions['<Parameter>'] += 1
        
        # Check for camelCase variables (e.g., fieldName, variableName)
        camel_case_pattern = r'\b[a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*\b'
        if re.search(camel_case_pattern, prompt_content):
            conventions['camelCase variables'] += 1
        
        # Check for snake_case variables (e.g., field_name, variable_name)
        snake_case_pattern = r'\b[a-z][a-z0-9_]*_[a-z0-9_]+\b'
        if re.search(snake_case_pattern, prompt_content):
            conventions['snake_case variables'] += 1
    
    return conventions

def create_workspace_dataframe(analysis_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Create a pandas DataFrame for workspace analysis
    
    Args:
        analysis_data: Analysis results dictionary
        
    Returns:
        DataFrame with workspace statistics
    """
    if not analysis_data:
        return pd.DataFrame()
    
    workspace_data = []
    
    for workspace_name, prompt_count in analysis_data['workspace_counts'].items():
        details = analysis_data['workspace_details'][workspace_name]
        percentage = (prompt_count / analysis_data['total_prompts']) * 100
        
        workspace_data.append({
            'Workspace': workspace_name,
            'Prompts': prompt_count,
            'Percentage': f"{percentage:.1f}%",
            'Agents': len(details['agents']),
            'Tools': len(details['tools']),
            'Avg Length': f"{details['total_chars'] / prompt_count:.0f}",
            'Total Chars': f"{details['total_chars']:,}"
        })
    
    return pd.DataFrame(workspace_data).sort_values('Prompts', ascending=False)

def create_convention_dataframe(convention_counts: Dict[str, int], total_prompts: int) -> pd.DataFrame:
    """
    Create a pandas DataFrame for convention analysis
    
    Args:
        convention_counts: Dictionary of convention counts
        total_prompts: Total number of prompts analyzed
        
    Returns:
        DataFrame with convention statistics
    """
    convention_data = []
    
    for convention, count in convention_counts.items():
        percentage = (count / total_prompts) * 100 if total_prompts > 0 else 0
        convention_data.append({
            'Convention': convention,
            'Count': count,
            'Percentage': f"{percentage:.1f}%",
            'Usage': f"{count}/{total_prompts}"
        })
    
    return pd.DataFrame(convention_data).sort_values('Count', ascending=False)

def create_prompt_length_chart(analysis_data: Dict[str, Any]):
    """
    Create a histogram of prompt lengths using Plotly
    
    Args:
        analysis_data: Analysis results dictionary
    """
    if not analysis_data or 'all_prompt_lengths' not in analysis_data:
        return None
    
    df = pd.DataFrame({
        'Prompt Length': analysis_data['all_prompt_lengths']
    })
    
    fig = px.histogram(
        df, 
        x='Prompt Length',
        nbins=30,
        title="Distribution of Prompt Lengths",
        labels={'Prompt Length': 'Characters', 'count': 'Number of Prompts'}
    )
    
    fig.update_layout(
        xaxis_title="Prompt Length (characters)",
        yaxis_title="Number of Prompts",
        showlegend=False
    )
    
    return fig

def create_workspace_chart(analysis_data: Dict[str, Any]):
    """
    Create a bar chart of top workspaces by prompt count
    
    Args:
        analysis_data: Analysis results dictionary
    """
    if not analysis_data:
        return None
    
    # Get top 10 workspaces
    sorted_workspaces = sorted(
        analysis_data['workspace_counts'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    workspaces = [item[0] for item in sorted_workspaces]
    counts = [item[1] for item in sorted_workspaces]
    
    fig = px.bar(
        x=workspaces,
        y=counts,
        title="Top 10 Workspaces by Prompt Count",
        labels={'x': 'Workspace', 'y': 'Number of Prompts'}
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False
    )
    
    return fig

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🏢 Prompt Analyzer</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📁 File Upload")
        
        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type=['json'],
            help="Upload your prompt recipes JSON file"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Load and analyze data
            analysis_data = load_and_analyze_json(uploaded_file)
            
            if analysis_data:
                st.session_state['analysis_data'] = analysis_data
                st.session_state['file_uploaded'] = True
            else:
                st.error("❌ Failed to load file")
                st.session_state['file_uploaded'] = False
        else:
            st.info("📋 Please upload a JSON file to begin analysis")
            st.session_state['file_uploaded'] = False
    
    # Main content area
    if st.session_state.get('file_uploaded', False) and 'analysis_data' in st.session_state:
        analysis_data = st.session_state['analysis_data']
        
        # Key Metrics Row
        st.header("📊 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📝 Total Prompts",
                value=f"{analysis_data['total_prompts']:,}",
                help="Total number of prompts in the dataset"
            )
        
        with col2:
            st.metric(
                label="🏢 Workspaces",
                value=f"{analysis_data['total_workspaces']:,}",
                help="Number of unique workspaces"
            )
        
        with col3:
            st.metric(
                label="🤖 Unique Agents",
                value=f"{analysis_data['total_agents']:,}",
                help="Number of unique agents"
            )
        
        with col4:
            st.metric(
                label="🛠️ Unique Tools",
                value=f"{analysis_data['total_tools']:,}",
                help="Number of unique tools"
            )
        
        # Prompt Statistics
        st.header("📈 Prompt Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📏 Average Length",
                value=f"{analysis_data['prompt_stats']['avg_length']:.0f} chars",
                help="Average prompt length in characters"
            )
        
        with col2:
            st.metric(
                label="📏 Shortest",
                value=f"{analysis_data['prompt_stats']['min_length']:,} chars",
                help="Shortest prompt length"
            )
        
        with col3:
            st.metric(
                label="📏 Longest",
                value=f"{analysis_data['prompt_stats']['max_length']:,} chars",
                help="Longest prompt length"
            )
        
        with col4:
            st.metric(
                label="📏 Total Characters",
                value=f"{analysis_data['prompt_stats']['total_chars']:,}",
                help="Total characters across all prompts"
            )
        
        # Prompt Convention Usage
        st.header("📚 Prompt Convention Usage")
        
        # Create convention dataframe
        convention_df = create_convention_dataframe(
            analysis_data['convention_counts'], 
            analysis_data['total_prompts']
        )
        
        if not convention_df.empty:
            st.dataframe(
                convention_df,
                use_container_width=True,
                hide_index=True
            )
        
        # Charts Section
        st.header("📊 Visualizations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            prompt_length_fig = create_prompt_length_chart(analysis_data)
            if prompt_length_fig:
                st.plotly_chart(prompt_length_fig, use_container_width=True)
        
        with col2:
            workspace_fig = create_workspace_chart(analysis_data)
            if workspace_fig:
                st.plotly_chart(workspace_fig, use_container_width=True)
        
        # Query Interface
        st.header("🔍 Prompt Content Query")
        
        with st.container():
            st.markdown('<div class="query-box">', unsafe_allow_html=True)
            
            query_type = st.selectbox(
                "Query Type",
                ["Text Search", "Regex Pattern", "Beam Conventions"],
                help="Choose how to search through prompts"
            )
            
            if query_type == "Text Search":
                query = st.text_input(
                    "Search for text in prompts",
                    placeholder="e.g., <topic>, @variable, ROLE:",
                    help="Enter text to search for in all prompts"
                )
                
                if query and st.button("🔍 Search"):
                    count, matches = search_prompts_for_pattern(analysis_data, query)
                    
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.success(f"✅ Found {count} prompts containing '{query}'")
                    
                    if matches:
                        st.subheader("📋 Matching Prompts")
                        for i, match in enumerate(matches[:10], 1):  # Show first 10
                            with st.expander(f"{i}. {match['tool']} ({match['workspace']})"):
                                st.write(f"**Agent:** {match['agent']}")
                                st.write(f"**Length:** {match['length']} characters")
                                st.write(f"**Preview:** {match['content_preview']}")
                    
                    if len(matches) > 10:
                        st.info(f"Showing first 10 of {len(matches)} matches")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            elif query_type == "Regex Pattern":
                pattern = st.text_input(
                    "Enter regex pattern",
                    placeholder="e.g., <topic>.*?</topic>",
                    help="Enter a regular expression pattern"
                )
                
                if pattern and st.button("🔍 Search"):
                    count, matches = search_prompts_with_regex(analysis_data, pattern)
                    
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.success(f"✅ Found {count} prompts matching pattern '{pattern}'")
                    
                    if matches:
                        st.subheader("📋 Matching Prompts")
                        for i, match in enumerate(matches[:10], 1):
                            with st.expander(f"{i}. {match['tool']} ({match['workspace']})"):
                                st.write(f"**Agent:** {match['agent']}")
                                st.write(f"**Length:** {match['length']} characters")
                                st.write(f"**Preview:** {match['content_preview']}")
                    
                    if len(matches) > 10:
                        st.info(f"Showing first 10 of {len(matches)} matches")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            elif query_type == "Beam Conventions":
                convention = st.selectbox(
                    "Select Beam Convention",
                    [
                        "<topic> and </topic> tags",
                        "<Topic> and <EndTopic> tags", 
                        "@topic keyword tags",
                        "ROLE: section",
                        "INSTRUCTIONS: section",
                        "VARIABLES: section",
                        "OUTPUT FORMAT: section",
                        "do not hallucinate",
                        "think step by step",
                        "follow formatting rules"
                    ],
                    help="Select a specific Beam convention to search for"
                )
                
                if convention and st.button("🔍 Search"):
                    # Map conventions to search patterns
                    convention_patterns = {
                        "<topic> and </topic> tags": r"<topic>.*?</topic>",
                        "<Topic> and <EndTopic> tags": r"<Topic>.*?</Topic>|<Topic>.*?<EndTopic>",
                        "@topic keyword tags": r"@topic|@endTopic|@EndTopic",
                        "ROLE: section": r"ROLE:",
                        "INSTRUCTIONS: section": r"INSTRUCTIONS:",
                        "VARIABLES: section": r"VARIABLES:",
                        "OUTPUT FORMAT: section": r"OUTPUT FORMAT:",
                        "do not hallucinate": r"do not hallucinate",
                        "think step by step": r"think step by step",
                        "follow formatting rules": r"follow formatting rules"
                    }
                    
                    pattern = convention_patterns.get(convention, convention)
                    count, matches = search_prompts_with_regex(analysis_data, pattern)
                    
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.success(f"✅ Found {count} prompts using '{convention}'")
                    
                    if matches:
                        st.subheader("📋 Matching Prompts")
                        for i, match in enumerate(matches[:10], 1):
                            with st.expander(f"{i}. {match['tool']} ({match['workspace']})"):
                                st.write(f"**Agent:** {match['agent']}")
                                st.write(f"**Length:** {match['length']} characters")
                                st.write(f"**Preview:** {match['content_preview']}")
                    
                    if len(matches) > 10:
                        st.info(f"Showing first 10 of {len(matches)} matches")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Export Section
        st.header("💾 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export Workspace Data"):
                df = create_workspace_dataframe(analysis_data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"workspace_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📋 Export Full Analysis"):
                analysis_json = json.dumps(analysis_data, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=analysis_json,
                    file_name=f"full_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    else:
        # Welcome message when no file is uploaded
        st.markdown("""
        ## 🎯 Welcome to Prompt Analyzer!
        
        This tool helps you analyze prompt engineering data from your JSON files.
        
        ### 📋 What you can do:
        - **Upload JSON files** containing prompt data
        - **View comprehensive statistics** about workspaces, agents, and tools
        - **Search through prompts** for specific patterns or conventions
        - **Analyze Beam conventions** usage across your prompts
        - **Export results** in CSV or JSON format
        - **Visualize data** with interactive charts
        
        ### 🚀 Getting Started:
        1. Use the sidebar to upload your JSON file
        2. View the key metrics and statistics
        3. Explore the top workspaces table
        4. Use the query interface to search for specific patterns
        5. Export your analysis results
        
        ### 📁 Expected File Format:
        Your JSON file should contain an array of objects with fields like:
        - `workspace_name`
        - `agent_name` 
        - `tool_name`
        - `prompt` (the actual prompt content)
        - `tool_category`
        """)
        
        # Show sample data structure
        with st.expander("📖 Sample JSON Structure"):
            st.json({
                "workspace_name": "Example Workspace",
                "agent_name": "Example Agent",
                "tool_name": "Example Tool",
                "prompt": "This is an example prompt content...",
                "tool_category": "Data and Analytics"
            })

if __name__ == "__main__":
    main() 
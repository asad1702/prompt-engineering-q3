#!/usr/bin/env python3
"""
Workspace Analyzer
Simple tool to analyze workspace names and prompt counts from JSON file
"""

import json
from collections import Counter
from typing import Dict, List, Any

def analyze_workspaces(json_file_path: str) -> Dict[str, Any]:
    """Analyze workspace names and prompt counts from JSON file"""
    
    try:
        # Load JSON data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Successfully loaded JSON file with {len(data)} prompts")
        
        # Extract workspace names
        workspace_counts = Counter()
        workspace_details = {}
        
        for item in data:
            workspace_name = item.get('workspace_name', 'Unknown Workspace')
            agent_name = item.get('agent_name', 'Unknown Agent')
            tool_name = item.get('tool_name', 'Unknown Tool')
            
            # Count workspace occurrences
            workspace_counts[workspace_name] += 1
            
            # Store details for each workspace
            if workspace_name not in workspace_details:
                workspace_details[workspace_name] = {
                    'total_prompts': 0,
                    'agents': set(),
                    'tools': set(),
                    'prompts': []
                }
            
            workspace_details[workspace_name]['total_prompts'] += 1
            workspace_details[workspace_name]['agents'].add(agent_name)
            workspace_details[workspace_name]['tools'].add(tool_name)
            
            # Store prompt info
            prompt_info = {
                'agent_name': agent_name,
                'tool_name': tool_name,
                'tool_category': item.get('tool_category', 'Unknown'),
                'prompt_length': len(item.get('prompt', ''))
            }
            workspace_details[workspace_name]['prompts'].append(prompt_info)
        
        # Convert sets to lists for JSON serialization
        for workspace_name in workspace_details:
            workspace_details[workspace_name]['agents'] = list(workspace_details[workspace_name]['agents'])
            workspace_details[workspace_name]['tools'] = list(workspace_details[workspace_name]['tools'])
        
        return {
            'total_prompts': len(data),
            'total_workspaces': len(workspace_counts),
            'workspace_counts': dict(workspace_counts),
            'workspace_details': workspace_details
        }
        
    except FileNotFoundError:
        print(f"❌ File not found: {json_file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return {}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def print_workspace_analysis(analysis: Dict[str, Any]):
    """Print workspace analysis in a formatted way"""
    
    if not analysis:
        print("❌ No analysis data available")
        return
    
    print("\n" + "="*60)
    print("🏢 WORKSPACE ANALYSIS REPORT")
    print("="*60)
    
    print(f"📊 Total Prompts: {analysis['total_prompts']}")
    print(f"🏢 Total Workspaces: {analysis['total_workspaces']}")
    
    print(f"\n📋 WORKSPACE BREAKDOWN:")
    print("-" * 40)
    
    # Sort workspaces by prompt count (descending)
    sorted_workspaces = sorted(
        analysis['workspace_counts'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    for i, (workspace_name, prompt_count) in enumerate(sorted_workspaces, 1):
        percentage = (prompt_count / analysis['total_prompts']) * 100
        print(f"{i:2d}. {workspace_name}")
        print(f"    📝 Prompts: {prompt_count} ({percentage:.1f}%)")
        
        # Show details for this workspace
        details = analysis['workspace_details'][workspace_name]
        print(f"    🤖 Agents: {len(details['agents'])}")
        print(f"    🛠️  Tools: {len(details['tools'])}")
        
        # Show top agents and tools
        if details['agents']:
            print(f"    📋 Top Agents: {', '.join(details['agents'][:3])}")
        if details['tools']:
            print(f"    🔧 Top Tools: {', '.join(details['tools'][:3])}")
        
        print()

def print_detailed_workspace_info(analysis: Dict[str, Any], workspace_name: str = None):
    """Print detailed information for a specific workspace or all workspaces"""
    
    if not analysis or 'workspace_details' not in analysis:
        print("❌ No detailed analysis available")
        return
    
    if workspace_name:
        # Show details for specific workspace
        if workspace_name in analysis['workspace_details']:
            details = analysis['workspace_details'][workspace_name]
            print(f"\n🔍 DETAILED ANALYSIS: {workspace_name}")
            print("=" * 60)
            print(f"📝 Total Prompts: {details['total_prompts']}")
            print(f"🤖 Unique Agents: {len(details['agents'])}")
            print(f"🛠️  Unique Tools: {len(details['tools'])}")
            
            print(f"\n🤖 AGENTS:")
            for agent in details['agents']:
                print(f"   • {agent}")
            
            print(f"\n🛠️  TOOLS:")
            for tool in details['tools']:
                print(f"   • {tool}")
            
            print(f"\n📊 PROMPT STATISTICS:")
            prompt_lengths = [p['prompt_length'] for p in details['prompts']]
            if prompt_lengths:
                avg_length = sum(prompt_lengths) / len(prompt_lengths)
                print(f"   • Average prompt length: {avg_length:.0f} characters")
                print(f"   • Shortest prompt: {min(prompt_lengths)} characters")
                print(f"   • Longest prompt: {max(prompt_lengths)} characters")
        else:
            print(f"❌ Workspace '{workspace_name}' not found")
    else:
        # Show summary for all workspaces
        print(f"\n📊 WORKSPACE SUMMARY:")
        print("=" * 60)
        
        for workspace_name, details in analysis['workspace_details'].items():
            print(f"\n🏢 {workspace_name}")
            print(f"   📝 Prompts: {details['total_prompts']}")
            print(f"   🤖 Agents: {len(details['agents'])}")
            print(f"   🛠️  Tools: {len(details['tools'])}")

def main():
    """Main function"""
    
    print("🏢 Workspace Analyzer")
    print("=" * 40)
    
    # JSON file path
    json_file = "Prompt Recipies - Prompts.json"
    
    # Analyze workspaces
    print(f"🔍 Analyzing workspaces from {json_file}...")
    analysis = analyze_workspaces(json_file)
    
    if not analysis:
        print("❌ Failed to analyze workspaces")
        return
    
    # Print basic analysis
    print_workspace_analysis(analysis)
    
    # Ask for detailed analysis
    print("\n" + "="*60)
    print("📋 DETAILED ANALYSIS OPTIONS:")
    print("1. Show detailed info for all workspaces")
    print("2. Show detailed info for specific workspace")
    print("3. Save analysis to JSON")
    print("4. Exit")
    
    while True:
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            print_detailed_workspace_info(analysis)
        elif choice == '2':
            workspace_name = input("Enter workspace name: ").strip()
            print_detailed_workspace_info(analysis, workspace_name)
        elif choice == '3':
            output_file = 'workspace_analysis.json'
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"✅ Analysis saved to {output_file}")
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Beam Convention Analyzer
Specialized tool for analyzing Beam platform prompt conventions and patterns
"""

import json
import re
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
from datetime import datetime
import pandas as pd

class BeamConventionAnalyzer:
    """Analyzer for Beam-specific prompt conventions and patterns"""
    
    def __init__(self):
        # Define all Beam conventions and patterns
        self.conventions = {
            # Context block patterns
            'context_blocks': {
                'topic_end_topic': {
                    'pattern': r'<Topic>.*?</Topic>|<Topic>.*?<EndTopic>',
                    'description': '<Topic> and </Topic> or <EndTopic> to guide the agent to context blocks',
                    'examples': ['<Topic>API Integration</Topic>', '<Topic>Data Analysis<EndTopic>']
                },
                'topic_lowercase': {
                    'pattern': r'<topic>.*?</topic>',
                    'description': '<topic> and </topic> to guide the agent to context blocks',
                    'examples': ['<topic>customer support</topic>']
                },
                'context_blocks': {
                    'pattern': r'<context>.*?</context>',
                    'description': '<context> and </context> for context blocks',
                    'examples': ['<context>Analyze this data</context>']
                },
                'generic_start_end': {
                    'pattern': r'<(\w+)Start>.*?</\1End>',
                    'description': '<xxxStart> and <xxxEnd> pattern',
                    'examples': ['<DataStart>customer data</DataEnd>']
                }
            },
            
            # Topic tag patterns
            'topic_tags': {
                'at_topic': {
                    'pattern': r'@\w+',
                    'description': '@topic to make keywords more unique and give it a "tag" for the ai',
                    'examples': ['@analysis', '@integration', '@support']
                },
                'at_end_topic': {
                    'pattern': r'@endTopic|@EndTopic',
                    'description': '@topic and @endTopic',
                    'examples': ['@endTopic', '@EndTopic']
                }
            },
            
            # Variable definition patterns
            'variables': {
                'curly_braces': {
                    'pattern': r'{{[^}]+}}',
                    'description': '{{topic}} to define variables',
                    'examples': ['{{customer_data}}', '{{api_documentation}}']
                },
                'camel_case': {
                    'pattern': r'"[^"]*[A-Z][^"]*"',
                    'description': 'CamelCase variable definitions like "variableTest"',
                    'examples': ['"variableTest"', '"customerData"']
                },
                'snake_case': {
                    'pattern': r'"[^"]*_[^"]*"',
                    'description': 'Snake_case variable definitions like "variable_test"',
                    'examples': ['"variable_test"', '"customer_data"']
                }
            },
            
            # Section patterns
            'sections': {
                'role': {
                    'pattern': r'^ROLE:',
                    'description': 'Role section definition',
                    'examples': ['ROLE:', 'ROLE: You are an expert...']
                },
                'instructions': {
                    'pattern': r'^INSTRUCTIONS:',
                    'description': 'Instructions section',
                    'examples': ['INSTRUCTIONS:', 'INSTRUCTIONS: 1. First...']
                },
                'general_rules': {
                    'pattern': r'^GENERAL RULES:',
                    'description': 'General rules section',
                    'examples': ['GENERAL RULES:', 'GENERAL RULES: - Do not...']
                },
                'variables': {
                    'pattern': r'^VARIABLES:',
                    'description': 'Variables section for structured outputs',
                    'examples': ['VARIABLES:', 'VARIABLES: - variable_name: type...']
                },
                'output_format': {
                    'pattern': r'^OUTPUT FORMAT:',
                    'description': 'Output format section',
                    'examples': ['OUTPUT FORMAT:', 'OUTPUT FORMAT: { "key": "value" }']
                },
                'context': {
                    'pattern': r'^CONTEXT:',
                    'description': 'Context section for beam input variables',
                    'examples': ['CONTEXT:', 'CONTEXT: {{variable_name}}']
                },
                'rules': {
                    'pattern': r'^RULES:',
                    'description': 'Rules section',
                    'examples': ['RULES:', 'RULES: 1. Think step by step...']
                }
            },
            
            # Anti-hallucination patterns
            'anti_hallucination': {
                'dont_hallucinate': {
                    'pattern': r'do not hallucinate|don\'t hallucinate',
                    'description': 'Anti-hallucination instructions',
                    'examples': ['do not hallucinate', "don't hallucinate"]
                },
                'no_assumptions': {
                    'pattern': r'do not make assumptions|don\'t make assumptions',
                    'description': 'No assumptions instructions',
                    'examples': ['do not make assumptions', "don't make assumptions"]
                },
                'be_precise': {
                    'pattern': r'be precise|work precise',
                    'description': 'Precision instructions',
                    'examples': ['be precise', 'work precise']
                },
                'step_by_step': {
                    'pattern': r'think step by step|step by step|step-by-step',
                    'description': 'Step-by-step thinking instructions',
                    'examples': ['think step by step', 'step by step']
                },
                'follow_formatting': {
                    'pattern': r'follow the formatting rules|follow formatting',
                    'description': 'Formatting rule instructions',
                    'examples': ['follow the formatting rules', 'follow formatting']
                }
            },
            
            # Markdown patterns
            'markdown': {
                'headers': {
                    'pattern': r'^#+\s+',
                    'description': 'Markdown headers',
                    'examples': ['# Header', '## Subheader']
                },
                'bold': {
                    'pattern': r'\*\*[^*]+\*\*',
                    'description': 'Markdown bold text',
                    'examples': ['**bold text**']
                },
                'italic': {
                    'pattern': r'\*[^*]+\*',
                    'description': 'Markdown italic text',
                    'examples': ['*italic text*']
                },
                'code_blocks': {
                    'pattern': r'```[\s\S]*?```',
                    'description': 'Markdown code blocks',
                    'examples': ['```json\n{"key": "value"}\n```']
                },
                'inline_code': {
                    'pattern': r'`[^`]+`',
                    'description': 'Markdown inline code',
                    'examples': ['`variable_name`']
                },
                'lists': {
                    'pattern': r'^\s*[-*+]\s+',
                    'description': 'Markdown bullet lists',
                    'examples': ['- item', '* item', '+ item']
                },
                'numbered_lists': {
                    'pattern': r'^\s*\d+\.\s+',
                    'description': 'Markdown numbered lists',
                    'examples': ['1. item', '2. item']
                }
            }
        }
    
    def load_prompts_from_json(self, json_file_path: str) -> List[Dict[str, Any]]:
        """Load prompts from JSON file"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # If it's a dict, look for common keys that might contain prompts
                for key in ['prompts', 'data', 'items', 'recipes']:
                    if key in data and isinstance(data[key], list):
                        return data[key]
                # If no list found, return the dict as a single item
                return [data]
            else:
                raise ValueError("Unexpected JSON structure")
                
        except Exception as e:
            print(f"❌ Error loading JSON file: {e}")
            return []
    
    def analyze_single_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single prompt for all Beam conventions"""
        
        # Extract prompt text
        prompt_text = self._extract_prompt_text(prompt_data)
        prompt_id = prompt_data.get('id', prompt_data.get('prompt_id', 'unknown'))
        
        analysis = {
            'prompt_id': prompt_id,
            'prompt_text': prompt_text,
            'conventions_found': {},
            'convention_counts': {},
            'overall_score': 0
        }
        
        # Analyze each convention category
        for category, conventions in self.conventions.items():
            analysis['conventions_found'][category] = {}
            analysis['convention_counts'][category] = 0
            
            for convention_name, convention_data in conventions.items():
                matches = self._find_convention_matches(prompt_text, convention_data['pattern'])
                
                analysis['conventions_found'][category][convention_name] = {
                    'found': len(matches) > 0,
                    'count': len(matches),
                    'matches': matches,
                    'description': convention_data['description'],
                    'examples': convention_data['examples']
                }
                
                if len(matches) > 0:
                    analysis['convention_counts'][category] += 1
        
        # Calculate overall Beam compliance score
        analysis['overall_score'] = self._calculate_compliance_score(analysis)
        
        return analysis
    
    def _extract_prompt_text(self, prompt_data: Dict[str, Any]) -> str:
        """Extract prompt text from various possible JSON structures"""
        
        # Common field names for prompt text
        text_fields = ['prompt', 'text', 'content', 'message', 'instruction', 'query', 'body']
        
        for field in text_fields:
            if field in prompt_data and prompt_data[field]:
                return str(prompt_data[field])
        
        # If no text field found, try to convert the entire data to string
        return str(prompt_data)
    
    def _find_convention_matches(self, text: str, pattern: str) -> List[str]:
        """Find all matches for a given convention pattern"""
        try:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            return matches if isinstance(matches, list) else [matches]
        except Exception:
            return []
    
    def _calculate_compliance_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall Beam compliance score"""
        score = 0
        max_score = 100
        
        # Weight different categories
        weights = {
            'context_blocks': 25,
            'topic_tags': 15,
            'variables': 20,
            'sections': 25,
            'anti_hallucination': 10,
            'markdown': 5
        }
        
        for category, weight in weights.items():
            if category in analysis['convention_counts']:
                category_score = analysis['convention_counts'][category] * weight
                score += min(category_score, weight)
        
        return min(max_score, score)
    
    def analyze_all_prompts(self, json_file_path: str) -> Dict[str, Any]:
        """Analyze all prompts in the JSON file"""
        
        print(f"🔍 Loading prompts from {json_file_path}...")
        prompts = self.load_prompts_from_json(json_file_path)
        
        if not prompts:
            return {"error": "No prompts found in JSON file"}
        
        print(f"✅ Loaded {len(prompts)} prompts")
        
        # Analyze each prompt
        all_analyses = []
        for prompt in prompts:
            analysis = self.analyze_single_prompt(prompt)
            all_analyses.append(analysis)
        
        # Generate comprehensive report
        report = self._generate_comprehensive_report(all_analyses)
        
        return report
    
    def _generate_comprehensive_report(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        
        total_prompts = len(analyses)
        
        # Aggregate statistics
        convention_usage = defaultdict(lambda: defaultdict(int))
        convention_matches = defaultdict(list)
        
        for analysis in analyses:
            for category, conventions in analysis['conventions_found'].items():
                for convention_name, convention_data in conventions.items():
                    if convention_data['found']:
                        convention_usage[category][convention_name] += 1
                        convention_matches[f"{category}_{convention_name}"].extend(convention_data['matches'])
        
        # Calculate percentages
        convention_percentages = {}
        for category, conventions in convention_usage.items():
            convention_percentages[category] = {}
            for convention_name, count in conventions.items():
                percentage = (count / total_prompts) * 100
                convention_percentages[category][convention_name] = {
                    'count': count,
                    'percentage': percentage
                }
        
        # Average scores
        avg_score = sum(a['overall_score'] for a in analyses) / total_prompts
        
        return {
            'summary': {
                'total_prompts': total_prompts,
                'average_compliance_score': round(avg_score, 2),
                'analysis_date': datetime.now().isoformat()
            },
            'convention_usage': convention_percentages,
            'convention_matches': dict(convention_matches),
            'individual_analyses': analyses
        }
    
    def answer_specific_question(self, question: str, json_file_path: str) -> Dict[str, Any]:
        """Answer specific questions about prompt conventions"""
        
        print(f"🔍 Analyzing: {question}")
        
        # Load and analyze prompts
        prompts = self.load_prompts_from_json(json_file_path)
        if not prompts:
            return {"error": "No prompts found"}
        
        # Analyze each prompt
        analyses = []
        for prompt in prompts:
            analysis = self.analyze_single_prompt(prompt)
            analyses.append(analysis)
        
        # Parse the question and find relevant conventions
        question_lower = question.lower()
        
        if 'topic' in question_lower and 'endtopic' in question_lower:
            return self._analyze_topic_endtopic_usage(analyses)
        elif 'context' in question_lower and 'block' in question_lower:
            return self._analyze_context_block_usage(analyses)
        elif 'variable' in question_lower:
            return self._analyze_variable_usage(analyses)
        elif 'section' in question_lower:
            return self._analyze_section_usage(analyses)
        elif 'markdown' in question_lower:
            return self._analyze_markdown_usage(analyses)
        elif 'anti-hallucination' in question_lower or 'hallucinate' in question_lower:
            return self._analyze_anti_hallucination_usage(analyses)
        else:
            return self._generate_comprehensive_report(analyses)
    
    def _analyze_topic_endtopic_usage(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze usage of Topic/EndTopic conventions"""
        
        topic_patterns = ['topic_end_topic', 'topic_lowercase']
        results = {
            'question': 'How many prompts use Topic/EndTopic conventions?',
            'patterns_analyzed': topic_patterns,
            'results': {}
        }
        
        for pattern in topic_patterns:
            count = 0
            examples = []
            
            for analysis in analyses:
                if (pattern in analysis['conventions_found'].get('context_blocks', {}) and 
                    analysis['conventions_found']['context_blocks'][pattern]['found']):
                    count += 1
                    examples.extend(analysis['conventions_found']['context_blocks'][pattern]['matches'])
            
            results['results'][pattern] = {
                'count': count,
                'percentage': (count / len(analyses)) * 100,
                'examples': examples[:5]  # Show first 5 examples
            }
        
        return results
    
    def _analyze_context_block_usage(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze usage of context blocks"""
        
        context_patterns = ['topic_end_topic', 'topic_lowercase', 'context_blocks', 'generic_start_end']
        results = {
            'question': 'How many prompts use context blocks?',
            'patterns_analyzed': context_patterns,
            'results': {}
        }
        
        for pattern in context_patterns:
            count = 0
            examples = []
            
            for analysis in analyses:
                if (pattern in analysis['conventions_found'].get('context_blocks', {}) and 
                    analysis['conventions_found']['context_blocks'][pattern]['found']):
                    count += 1
                    examples.extend(analysis['conventions_found']['context_blocks'][pattern]['matches'])
            
            results['results'][pattern] = {
                'count': count,
                'percentage': (count / len(analyses)) * 100,
                'examples': examples[:5]
            }
        
        return results
    
    def _analyze_variable_usage(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze variable definition patterns"""
        
        variable_patterns = ['curly_braces', 'camel_case', 'snake_case']
        results = {
            'question': 'How many prompts use different variable definition patterns?',
            'patterns_analyzed': variable_patterns,
            'results': {}
        }
        
        for pattern in variable_patterns:
            count = 0
            examples = []
            
            for analysis in analyses:
                if (pattern in analysis['conventions_found'].get('variables', {}) and 
                    analysis['conventions_found']['variables'][pattern]['found']):
                    count += 1
                    examples.extend(analysis['conventions_found']['variables'][pattern]['matches'])
            
            results['results'][pattern] = {
                'count': count,
                'percentage': (count / len(analyses)) * 100,
                'examples': examples[:5]
            }
        
        return results
    
    def _analyze_section_usage(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze section usage patterns"""
        
        section_patterns = ['role', 'instructions', 'general_rules', 'variables', 'output_format', 'context', 'rules']
        results = {
            'question': 'How many prompts use different sections?',
            'patterns_analyzed': section_patterns,
            'results': {}
        }
        
        for pattern in section_patterns:
            count = 0
            
            for analysis in analyses:
                if (pattern in analysis['conventions_found'].get('sections', {}) and 
                    analysis['conventions_found']['sections'][pattern]['found']):
                    count += 1
            
            results['results'][pattern] = {
                'count': count,
                'percentage': (count / len(analyses)) * 100
            }
        
        return results
    
    def _analyze_markdown_usage(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze markdown formatting usage"""
        
        markdown_patterns = ['headers', 'bold', 'italic', 'code_blocks', 'inline_code', 'lists', 'numbered_lists']
        results = {
            'question': 'How many prompts use markdown formatting?',
            'patterns_analyzed': markdown_patterns,
            'results': {}
        }
        
        for pattern in markdown_patterns:
            count = 0
            examples = []
            
            for analysis in analyses:
                if (pattern in analysis['conventions_found'].get('markdown', {}) and 
                    analysis['conventions_found']['markdown'][pattern]['found']):
                    count += 1
                    examples.extend(analysis['conventions_found']['markdown'][pattern]['matches'])
            
            results['results'][pattern] = {
                'count': count,
                'percentage': (count / len(analyses)) * 100,
                'examples': examples[:3]
            }
        
        return results
    
    def _analyze_anti_hallucination_usage(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze anti-hallucination pattern usage"""
        
        anti_hallucination_patterns = ['dont_hallucinate', 'no_assumptions', 'be_precise', 'step_by_step', 'follow_formatting']
        results = {
            'question': 'How many prompts use anti-hallucination patterns?',
            'patterns_analyzed': anti_hallucination_patterns,
            'results': {}
        }
        
        for pattern in anti_hallucination_patterns:
            count = 0
            examples = []
            
            for analysis in analyses:
                if (pattern in analysis['conventions_found'].get('anti_hallucination', {}) and 
                    analysis['conventions_found']['anti_hallucination'][pattern]['found']):
                    count += 1
                    examples.extend(analysis['conventions_found']['anti_hallucination'][pattern]['matches'])
            
            results['results'][pattern] = {
                'count': count,
                'percentage': (count / len(analyses)) * 100,
                'examples': examples[:3]
            }
        
        return results

def print_analysis_results(results: Dict[str, Any]):
    """Print analysis results in a formatted way"""
    
    if 'error' in results:
        print(f"❌ {results['error']}")
        return
    
    if 'question' in results:
        # Specific question analysis
        print(f"\n🔍 {results['question']}")
        print("=" * 60)
        
        for pattern, data in results['results'].items():
            print(f"\n📊 {pattern.replace('_', ' ').title()}:")
            print(f"   • Count: {data['count']} prompts")
            print(f"   • Percentage: {data['percentage']:.1f}%")
            
            if 'examples' in data and data['examples']:
                print(f"   • Examples: {', '.join(data['examples'][:3])}")
    else:
        # Comprehensive analysis
        print(f"\n🚀 BEAM CONVENTION ANALYSIS REPORT")
        print("=" * 60)
        print(f"📊 Total Prompts: {results['summary']['total_prompts']}")
        print(f"📈 Average Compliance Score: {results['summary']['average_compliance_score']}/100")
        
        print(f"\n📋 CONVENTION USAGE SUMMARY:")
        for category, conventions in results['convention_usage'].items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for convention, data in conventions.items():
                print(f"   • {convention.replace('_', ' ').title()}: {data['count']} ({data['percentage']:.1f}%)")

def main():
    """Main function for interactive analysis"""
    
    analyzer = BeamConventionAnalyzer()
    
    print("🚀 Beam Convention Analyzer")
    print("=" * 40)
    
    # Get JSON file path
    json_file = input("Enter the path to your JSON file (or press Enter for 'Prompt Recipies - Prompts.json'): ").strip()
    if not json_file:
        json_file = "Prompt Recipies - Prompts.json"
    
    try:
        while True:
            print(f"\n📊 ANALYSIS OPTIONS:")
            print("1. How many prompts use Topic/EndTopic conventions?")
            print("2. How many prompts use context blocks?")
            print("3. How many prompts use different variable patterns?")
            print("4. How many prompts use different sections?")
            print("5. How many prompts use markdown formatting?")
            print("6. How many prompts use anti-hallucination patterns?")
            print("7. Comprehensive analysis")
            print("8. Custom question")
            print("9. Exit")
            
            choice = input("\nSelect option (1-9): ").strip()
            
            if choice == '1':
                results = analyzer.answer_specific_question("How many prompts use Topic/EndTopic conventions?", json_file)
                print_analysis_results(results)
            
            elif choice == '2':
                results = analyzer.answer_specific_question("How many prompts use context blocks?", json_file)
                print_analysis_results(results)
            
            elif choice == '3':
                results = analyzer.answer_specific_question("How many prompts use different variable patterns?", json_file)
                print_analysis_results(results)
            
            elif choice == '4':
                results = analyzer.answer_specific_question("How many prompts use different sections?", json_file)
                print_analysis_results(results)
            
            elif choice == '5':
                results = analyzer.answer_specific_question("How many prompts use markdown formatting?", json_file)
                print_analysis_results(results)
            
            elif choice == '6':
                results = analyzer.answer_specific_question("How many prompts use anti-hallucination patterns?", json_file)
                print_analysis_results(results)
            
            elif choice == '7':
                results = analyzer.analyze_all_prompts(json_file)
                print_analysis_results(results)
                
                # Save results
                save = input("\nSave results to JSON? (y/n): ").strip().lower()
                if save == 'y':
                    with open('beam_convention_analysis.json', 'w') as f:
                        json.dump(results, f, indent=2)
                    print("✅ Results saved to 'beam_convention_analysis.json'")
            
            elif choice == '8':
                question = input("Enter your custom question: ").strip()
                results = analyzer.answer_specific_question(question, json_file)
                print_analysis_results(results)
            
            elif choice == '9':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option. Please try again.")
    
    except FileNotFoundError:
        print(f"❌ File not found: {json_file}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 
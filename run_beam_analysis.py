#!/usr/bin/env python3
"""
Simple script to run Beam Convention Analysis
"""

from beam_convention_analyzer import BeamConventionAnalyzer, print_analysis_results
import json

def run_quick_analysis():
    """Run a quick analysis of your Beam prompts"""
    
    # Initialize analyzer
    analyzer = BeamConventionAnalyzer()
    
    # Your JSON file
    json_file = "Prompt Recipies - Prompts.json"
    
    print("🚀 Beam Convention Analyzer - Quick Analysis")
    print("=" * 50)
    
    try:
        # Answer your specific question about Topic/EndTopic
        print("\n🔍 Question: How many prompts use the <Topic> and <EndTopic> convention?")
        results = analyzer.answer_specific_question(
            "How many prompts use Topic/EndTopic conventions?", 
            json_file
        )
        print_analysis_results(results)
        
        # Additional useful questions
        print("\n" + "="*50)
        print("🔍 Question: How many prompts use context blocks?")
        results = analyzer.answer_specific_question(
            "How many prompts use context blocks?", 
            json_file
        )
        print_analysis_results(results)
        
        print("\n" + "="*50)
        print("🔍 Question: How many prompts use different variable patterns?")
        results = analyzer.answer_specific_question(
            "How many prompts use different variable patterns?", 
            json_file
        )
        print_analysis_results(results)
        
        print("\n" + "="*50)
        print("🔍 Question: How many prompts use anti-hallucination patterns?")
        results = analyzer.answer_specific_question(
            "How many prompts use anti-hallucination patterns?", 
            json_file
        )
        print_analysis_results(results)
        
        # Save comprehensive results
        print("\n" + "="*50)
        print("💾 Saving comprehensive analysis...")
        comprehensive_results = analyzer.analyze_all_prompts(json_file)
        
        with open('beam_comprehensive_analysis.json', 'w') as f:
            json.dump(comprehensive_results, f, indent=2)
        
        print("✅ Comprehensive analysis saved to 'beam_comprehensive_analysis.json'")
        
        # Print summary
        print("\n📊 SUMMARY:")
        print(f"Total prompts analyzed: {comprehensive_results['summary']['total_prompts']}")
        print(f"Average compliance score: {comprehensive_results['summary']['average_compliance_score']}/100")
        
    except FileNotFoundError:
        print(f"❌ File not found: {json_file}")
        print("Please make sure your JSON file is in the same directory as this script.")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

def run_custom_question():
    """Run a custom question analysis"""
    
    analyzer = BeamConventionAnalyzer()
    json_file = "Prompt Recipies - Prompts.json"
    
    print("\n🔍 CUSTOM QUESTION ANALYSIS")
    print("=" * 40)
    
    # Example custom questions you can ask
    custom_questions = [
        "How many prompts use the <xxxStart> and <xxxEnd> pattern?",
        "How many prompts use @topic tags?",
        "How many prompts use {{variable}} patterns?",
        "How many prompts have ROLE sections?",
        "How many prompts use markdown formatting?",
        "How many prompts include 'think step by step' instructions?"
    ]
    
    print("Example questions you can ask:")
    for i, question in enumerate(custom_questions, 1):
        print(f"{i}. {question}")
    
    print("\nOr enter your own question:")
    question = input("Your question: ").strip()
    
    if question:
        try:
            results = analyzer.answer_specific_question(question, json_file)
            print_analysis_results(results)
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function"""
    print("🚀 Beam Convention Analyzer")
    print("=" * 40)
    print("Choose an option:")
    print("1. Run quick analysis (recommended)")
    print("2. Ask custom question")
    print("3. Run interactive mode")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == '1':
        run_quick_analysis()
    elif choice == '2':
        run_custom_question()
    elif choice == '3':
        from beam_convention_analyzer import main as interactive_main
        interactive_main()
    elif choice == '4':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid option. Please run the script again.")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Workspace Analyzer GUI
User-friendly Tkinter interface for workspace analysis
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
from collections import Counter
from typing import Dict, List, Any
import threading
import time

class WorkspaceAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🏢 Workspace Analyzer")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.analysis_data = {}
        self.current_workspace = None
        
        # Create GUI components
        self.create_widgets()
        
        # Show loading screen and load default file
        self.show_loading_screen()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(self.main_frame, text="🏢 Workspace Analyzer", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(self.main_frame, text="📁 File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="JSON File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.file_path_var = tk.StringVar(value="Prompt Recipies - Prompts.json")
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(file_frame, text="Load & Analyze", command=self.load_and_analyze).grid(row=0, column=3)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to analyze")
        self.status_label = ttk.Label(file_frame, textvariable=self.status_var, 
                                     foreground='blue')
        self.status_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        
        # Main content area
        content_frame = ttk.Frame(self.main_frame)
        content_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel - Workspace list
        left_panel = ttk.LabelFrame(content_frame, text="📋 Workspaces", padding="10")
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        
        # Workspace listbox
        self.workspace_listbox = tk.Listbox(left_panel, height=15, font=('Arial', 10))
        self.workspace_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.workspace_listbox.bind('<<ListboxSelect>>', self.on_workspace_select)
        
        # Scrollbar for workspace list
        workspace_scrollbar = ttk.Scrollbar(left_panel, orient=tk.VERTICAL, 
                                           command=self.workspace_listbox.yview)
        workspace_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.workspace_listbox.configure(yscrollcommand=workspace_scrollbar.set)
        
        # Right panel - Details
        right_panel = ttk.LabelFrame(content_frame, text="📊 Analysis Details", padding="10")
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)
        
        # Notebook for different views
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Home tab (Dashboard)
        self.home_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.home_frame, text="🏠 Home")
        self.home_frame.columnconfigure(0, weight=1)
        self.home_frame.columnconfigure(1, weight=1)
        self.home_frame.rowconfigure(1, weight=1)
        
        # Create home dashboard widgets
        self.create_home_dashboard()
        
        # Summary tab
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="📈 Summary")
        self.summary_frame.columnconfigure(0, weight=1)
        self.summary_frame.rowconfigure(0, weight=1)
        
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, 
                                                     wrap=tk.WORD, font=('Arial', 10))
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Workspace details tab
        self.details_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.details_frame, text="🏢 Workspace Details")
        self.details_frame.columnconfigure(0, weight=1)
        self.details_frame.rowconfigure(0, weight=1)
        
        self.details_text = scrolledtext.ScrolledText(self.details_frame, 
                                                     wrap=tk.WORD, font=('Arial', 10))
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Statistics tab
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📊 Statistics")
        self.stats_frame.columnconfigure(0, weight=1)
        self.stats_frame.rowconfigure(0, weight=1)
        
        self.stats_text = scrolledtext.ScrolledText(self.stats_frame, 
                                                   wrap=tk.WORD, font=('Arial', 10))
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bottom buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="💾 Save Analysis", 
                  command=self.save_analysis).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🔄 Refresh", 
                  command=self.load_and_analyze).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📋 Export to CSV", 
                  command=self.export_to_csv).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="❌ Exit", 
                  command=self.root.quit).pack(side=tk.RIGHT)
    
    def create_home_dashboard(self):
        """Create the home dashboard with key statistics"""
        
        # Top stats frame
        top_stats_frame = ttk.Frame(self.home_frame)
        top_stats_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        top_stats_frame.columnconfigure(0, weight=1)
        top_stats_frame.columnconfigure(1, weight=1)
        top_stats_frame.columnconfigure(2, weight=1)
        top_stats_frame.columnconfigure(3, weight=1)
        
        # Key metrics cards
        self.create_metric_card(top_stats_frame, "📊 Total Prompts", "0", 0, 0)
        self.create_metric_card(top_stats_frame, "🏢 Workspaces", "0", 0, 1)
        self.create_metric_card(top_stats_frame, "🤖 Total Agents", "0", 0, 2)
        self.create_metric_card(top_stats_frame, "🛠️ Total Tools", "0", 0, 3)
        
        # Left column - Top workspaces
        left_col = ttk.LabelFrame(self.home_frame, text="🏆 Top Workspaces", padding="10")
        left_col.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_col.columnconfigure(0, weight=1)
        left_col.rowconfigure(1, weight=1)
        
        self.top_workspaces_text = scrolledtext.ScrolledText(left_col, 
                                                           wrap=tk.WORD, 
                                                           font=('Arial', 10),
                                                           height=15)
        self.top_workspaces_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Right column - Quick stats
        right_col = ttk.LabelFrame(self.home_frame, text="📈 Quick Statistics", padding="10")
        right_col.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_col.columnconfigure(0, weight=1)
        right_col.rowconfigure(1, weight=1)
        
        self.quick_stats_text = scrolledtext.ScrolledText(right_col, 
                                                        wrap=tk.WORD, 
                                                        font=('Arial', 10),
                                                        height=15)
        self.quick_stats_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def create_metric_card(self, parent, title, value, row, col):
        """Create a metric card widget"""
        card_frame = ttk.Frame(parent, relief="raised", borderwidth=2)
        card_frame.grid(row=row, column=col, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        card_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(card_frame, text=title, font=('Arial', 10, 'bold'))
        title_label.grid(row=0, column=0, pady=(10, 5))
        
        # Value
        value_label = ttk.Label(card_frame, text=value, font=('Arial', 16, 'bold'), 
                               foreground='blue')
        value_label.grid(row=1, column=0, pady=(0, 10))
        
        # Store reference for updating
        if not hasattr(self, 'metric_labels'):
            self.metric_labels = {}
        self.metric_labels[title] = value_label
    
    def show_loading_screen(self):
        """Show loading screen while initializing"""
        # Create loading window
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("Loading...")
        self.loading_window.geometry("400x200")
        self.loading_window.resizable(False, False)
        self.loading_window.transient(self.root)
        self.loading_window.grab_set()
        
        # Center the loading window
        self.loading_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()//2 - 200,
            self.root.winfo_rooty() + self.root.winfo_height()//2 - 100
        ))
        
        # Loading content
        loading_frame = ttk.Frame(self.loading_window, padding="20")
        loading_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(loading_frame, text="🏢 Workspace Analyzer", 
                               font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Loading message
        self.loading_label = ttk.Label(loading_frame, text="Initializing...", 
                                      font=('Arial', 10))
        self.loading_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(loading_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        self.progress_bar.start()
        
        # Start loading process
        self.load_default_file_with_progress()
    
    def load_default_file_with_progress(self):
        """Load default file with progress updates"""
        def loading_thread():
            try:
                # Update loading message
                self.loading_label.config(text="Loading default file...")
                self.root.update()
                time.sleep(0.5)
                
                # Try to load and analyze
                if self.analyze_workspaces(self.file_path_var.get()):
                    self.loading_label.config(text="✅ Analysis complete!")
                    time.sleep(1)
                    self.update_display()
                else:
                    self.loading_label.config(text="⚠️ Default file not found")
                    time.sleep(1)
                
                # Close loading window
                self.loading_window.destroy()
                
            except Exception as e:
                self.loading_label.config(text=f"❌ Error: {str(e)}")
                time.sleep(2)
                self.loading_window.destroy()
        
        thread = threading.Thread(target=loading_thread)
        thread.daemon = True
        thread.start()
    
    def browse_file(self):
        """Browse for JSON file"""
        filename = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
    
    def load_and_analyze(self):
        """Load and analyze the selected file"""
        def analyze_thread():
            self.status_var.set("🔄 Analyzing...")
            self.root.update()
            
            if self.analyze_workspaces(self.file_path_var.get()):
                self.status_var.set("✅ Analysis complete")
                self.update_display()
            else:
                self.status_var.set("❌ Analysis failed")
        
        # Run analysis in separate thread to prevent GUI freezing
        thread = threading.Thread(target=analyze_thread)
        thread.daemon = True
        thread.start()
    
    def analyze_workspaces(self, json_file_path: str) -> bool:
        """Analyze workspace names and prompt counts from JSON file"""
        try:
            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
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
            
            self.analysis_data = {
                'total_prompts': len(data),
                'total_workspaces': len(workspace_counts),
                'workspace_counts': dict(workspace_counts),
                'workspace_details': workspace_details
            }
            
            return True
            
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {json_file_path}")
            return False
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"JSON decode error: {e}")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            return False
    
    def update_display(self):
        """Update all display elements"""
        self.update_metric_cards()
        self.update_home_dashboard()
        self.update_workspace_list()
        self.update_summary()
        self.update_statistics()
    
    def update_metric_cards(self):
        """Update the metric cards on home page"""
        if not self.analysis_data:
            return
        
        # Calculate totals
        total_agents = sum(len(details['agents']) for details in self.analysis_data['workspace_details'].values())
        total_tools = sum(len(details['tools']) for details in self.analysis_data['workspace_details'].values())
        
        # Update metric cards
        self.metric_labels["📊 Total Prompts"].config(text=str(self.analysis_data['total_prompts']))
        self.metric_labels["🏢 Workspaces"].config(text=str(self.analysis_data['total_workspaces']))
        self.metric_labels["🤖 Total Agents"].config(text=str(total_agents))
        self.metric_labels["🛠️ Total Tools"].config(text=str(total_tools))
    
    def update_home_dashboard(self):
        """Update home dashboard content"""
        if not self.analysis_data:
            return
        
        # Update top workspaces
        self.update_top_workspaces()
        
        # Update quick stats
        self.update_quick_stats()
    
    def update_top_workspaces(self):
        """Update top workspaces section"""
        self.top_workspaces_text.delete(1.0, tk.END)
        
        # Sort workspaces by prompt count
        sorted_workspaces = sorted(
            self.analysis_data['workspace_counts'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        content = "🏆 TOP WORKSPACES BY PROMPT COUNT\n"
        content += "=" * 50 + "\n\n"
        
        for i, (workspace_name, prompt_count) in enumerate(sorted_workspaces[:10], 1):
            percentage = (prompt_count / self.analysis_data['total_prompts']) * 100
            details = self.analysis_data['workspace_details'][workspace_name]
            
            content += f"{i:2d}. {workspace_name}\n"
            content += f"    📝 Prompts: {prompt_count} ({percentage:.1f}%)\n"
            content += f"    🤖 Agents: {len(details['agents'])}\n"
            content += f"    🛠️  Tools: {len(details['tools'])}\n\n"
        
        self.top_workspaces_text.insert(tk.END, content)
    
    def update_quick_stats(self):
        """Update quick statistics section"""
        self.quick_stats_text.delete(1.0, tk.END)
        
        # Calculate statistics
        prompt_counts = list(self.analysis_data['workspace_counts'].values())
        avg_prompts = sum(prompt_counts) / len(prompt_counts)
        max_prompts = max(prompt_counts)
        min_prompts = min(prompt_counts)
        
        total_agents = sum(len(details['agents']) for details in self.analysis_data['workspace_details'].values())
        total_tools = sum(len(details['tools']) for details in self.analysis_data['workspace_details'].values())
        
        # Prompt length statistics
        all_prompt_lengths = []
        for details in self.analysis_data['workspace_details'].values():
            all_prompt_lengths.extend([p['prompt_length'] for p in details['prompts']])
        
        content = "📈 QUICK STATISTICS\n"
        content += "=" * 30 + "\n\n"
        
        content += f"📊 PROMPT DISTRIBUTION:\n"
        content += f"• Average per workspace: {avg_prompts:.1f}\n"
        content += f"• Maximum: {max_prompts}\n"
        content += f"• Minimum: {min_prompts}\n\n"
        
        content += f"🤖 AGENT STATISTICS:\n"
        content += f"• Total unique agents: {total_agents}\n"
        content += f"• Average per workspace: {total_agents / len(self.analysis_data['workspace_details']):.1f}\n\n"
        
        content += f"🛠️  TOOL STATISTICS:\n"
        content += f"• Total unique tools: {total_tools}\n"
        content += f"• Average per workspace: {total_tools / len(self.analysis_data['workspace_details']):.1f}\n\n"
        
        if all_prompt_lengths:
            avg_length = sum(all_prompt_lengths) / len(all_prompt_lengths)
            content += f"📝 PROMPT LENGTH:\n"
            content += f"• Average: {avg_length:.0f} chars\n"
            content += f"• Shortest: {min(all_prompt_lengths)} chars\n"
            content += f"• Longest: {max(all_prompt_lengths)} chars\n"
            content += f"• Total: {sum(all_prompt_lengths):,} chars\n"
        
        self.quick_stats_text.insert(tk.END, content)
    
    def update_workspace_list(self):
        """Update workspace listbox"""
        self.workspace_listbox.delete(0, tk.END)
        
        if not self.analysis_data:
            return
        
        # Sort workspaces by prompt count (descending)
        sorted_workspaces = sorted(
            self.analysis_data['workspace_counts'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for workspace_name, prompt_count in sorted_workspaces:
            percentage = (prompt_count / self.analysis_data['total_prompts']) * 100
            display_text = f"{workspace_name} ({prompt_count} prompts, {percentage:.1f}%)"
            self.workspace_listbox.insert(tk.END, display_text)
    
    def update_summary(self):
        """Update summary tab"""
        self.summary_text.delete(1.0, tk.END)
        
        if not self.analysis_data:
            self.summary_text.insert(tk.END, "No analysis data available")
            return
        
        summary = f"""🏢 WORKSPACE ANALYSIS SUMMARY
{'='*60}

📊 OVERALL STATISTICS:
• Total Prompts: {self.analysis_data['total_prompts']}
• Total Workspaces: {self.analysis_data['total_workspaces']}

📋 WORKSPACE BREAKDOWN:
"""
        
        # Sort workspaces by prompt count
        sorted_workspaces = sorted(
            self.analysis_data['workspace_counts'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        for i, (workspace_name, prompt_count) in enumerate(sorted_workspaces, 1):
            percentage = (prompt_count / self.analysis_data['total_prompts']) * 100
            details = self.analysis_data['workspace_details'][workspace_name]
            
            summary += f"""
{i}. {workspace_name}
   📝 Prompts: {prompt_count} ({percentage:.1f}%)
   🤖 Agents: {len(details['agents'])}
   🛠️  Tools: {len(details['tools'])}
"""
        
        self.summary_text.insert(tk.END, summary)
    
    def update_statistics(self):
        """Update statistics tab"""
        self.stats_text.delete(1.0, tk.END)
        
        if not self.analysis_data:
            self.stats_text.insert(tk.END, "No analysis data available")
            return
        
        stats = f"""📊 DETAILED STATISTICS
{'='*60}

📈 PROMPT DISTRIBUTION:
"""
        
        # Calculate statistics
        prompt_counts = list(self.analysis_data['workspace_counts'].values())
        avg_prompts = sum(prompt_counts) / len(prompt_counts)
        max_prompts = max(prompt_counts)
        min_prompts = min(prompt_counts)
        
        stats += f"""• Average prompts per workspace: {avg_prompts:.1f}
• Maximum prompts in a workspace: {max_prompts}
• Minimum prompts in a workspace: {min_prompts}

📊 WORKSPACE ANALYSIS:
"""
        
        # Agent and tool statistics
        total_agents = sum(len(details['agents']) for details in self.analysis_data['workspace_details'].values())
        total_tools = sum(len(details['tools']) for details in self.analysis_data['workspace_details'].values())
        
        stats += f"""• Total unique agents across all workspaces: {total_agents}
• Total unique tools across all workspaces: {total_tools}
• Average agents per workspace: {total_agents / len(self.analysis_data['workspace_details']):.1f}
• Average tools per workspace: {total_tools / len(self.analysis_data['workspace_details']):.1f}

📋 PROMPT LENGTH STATISTICS:
"""
        
        # Prompt length statistics
        all_prompt_lengths = []
        for details in self.analysis_data['workspace_details'].values():
            all_prompt_lengths.extend([p['prompt_length'] for p in details['prompts']])
        
        if all_prompt_lengths:
            avg_length = sum(all_prompt_lengths) / len(all_prompt_lengths)
            stats += f"""• Average prompt length: {avg_length:.0f} characters
• Shortest prompt: {min(all_prompt_lengths)} characters
• Longest prompt: {max(all_prompt_lengths)} characters
• Total characters across all prompts: {sum(all_prompt_lengths):,}
"""
        
        self.stats_text.insert(tk.END, stats)
    
    def on_workspace_select(self, event):
        """Handle workspace selection"""
        selection = self.workspace_listbox.curselection()
        if not selection:
            return
        
        # Get selected workspace name
        selected_text = self.workspace_listbox.get(selection[0])
        workspace_name = selected_text.split(' (')[0]  # Extract name before parentheses
        
        self.current_workspace = workspace_name
        self.update_workspace_details()
    
    def update_workspace_details(self):
        """Update workspace details tab"""
        self.details_text.delete(1.0, tk.END)
        
        if not self.current_workspace or not self.analysis_data:
            self.details_text.insert(tk.END, "Select a workspace to view details")
            return
        
        if self.current_workspace not in self.analysis_data['workspace_details']:
            self.details_text.insert(tk.END, f"Workspace '{self.current_workspace}' not found")
            return
        
        details = self.analysis_data['workspace_details'][self.current_workspace]
        
        details_text = f"""🔍 DETAILED ANALYSIS: {self.current_workspace}
{'='*60}

📊 BASIC INFORMATION:
• Total Prompts: {details['total_prompts']}
• Unique Agents: {len(details['agents'])}
• Unique Tools: {len(details['tools'])}

🤖 AGENTS:
"""
        
        for agent in details['agents']:
            details_text += f"   • {agent}\n"
        
        details_text += f"""
🛠️  TOOLS:
"""
        
        for tool in details['tools']:
            details_text += f"   • {tool}\n"
        
        details_text += f"""
📊 PROMPT STATISTICS:
"""
        
        prompt_lengths = [p['prompt_length'] for p in details['prompts']]
        if prompt_lengths:
            avg_length = sum(prompt_lengths) / len(prompt_lengths)
            details_text += f"""• Average prompt length: {avg_length:.0f} characters
• Shortest prompt: {min(prompt_lengths)} characters
• Longest prompt: {max(prompt_lengths)} characters
• Total characters: {sum(prompt_lengths):,}

📋 INDIVIDUAL PROMPTS:
"""
            
            for i, prompt in enumerate(details['prompts'], 1):
                details_text += f"""
{i}. {prompt['tool_name']}
   Agent: {prompt['agent_name']}
   Category: {prompt['tool_category']}
   Length: {prompt['prompt_length']} characters
"""
        
        self.details_text.insert(tk.END, details_text)
    
    def save_analysis(self):
        """Save analysis to JSON file"""
        if not self.analysis_data:
            messagebox.showwarning("Warning", "No analysis data to save")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Save Analysis",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.analysis_data, f, indent=2)
                messagebox.showinfo("Success", f"Analysis saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
    
    def export_to_csv(self):
        """Export analysis to CSV format"""
        if not self.analysis_data:
            messagebox.showwarning("Warning", "No analysis data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Workspace', 'Prompts', 'Percentage', 'Agents', 'Tools'])
                    
                    for workspace_name, prompt_count in self.analysis_data['workspace_counts'].items():
                        percentage = (prompt_count / self.analysis_data['total_prompts']) * 100
                        details = self.analysis_data['workspace_details'][workspace_name]
                        writer.writerow([
                            workspace_name,
                            prompt_count,
                            f"{percentage:.1f}%",
                            len(details['agents']),
                            len(details['tools'])
                        ])
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

def main():
    """Main function"""
    root = tk.Tk()
    app = WorkspaceAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
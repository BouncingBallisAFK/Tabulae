#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, font, filedialog, messagebox, colorchooser
from tabulae import Interpreter
import io
from contextlib import redirect_stdout
import re

class TabulaeGUI:
    def __init__(self, root):
        self.root = root
        self.repl_interpreter = Interpreter()
        self.editor_interpreter = Interpreter()
        self.command_history = []
        self.history_index = -1
        self.current_file = None
        self.custom_colors = {
            'bg': "#f0f0f0",
            'fg': "black",
            'text_bg': "#ffffff",
            'text_fg': "black",
            'output_bg': "#f8f8f8",
            'output_fg': "black",
            'button_bg': "#c0c0c0",
            'button_fg': "black",
            'tree_bg': "#ffffff",
            'tree_fg': "black",
            'tree_heading_bg': "#e0e0e0",
            'select_bg': "#347083",
            'syntax_command': "#fff3cd"  # Soft yellow for commands
        }
        
        self.initialize_ui()
        self.apply_theme()  # Apply default theme
        
    def initialize_ui(self):
        self.root.title("Tabulae IDE")
        self.root.geometry("1200x800")
        self.style = ttk.Style()
        
        # Create notebook with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Initialize tabs
        self.setup_repl_tab()
        self.setup_editor_tab()
        
        # Setup menu (keeping only Custom Theme)
        self.setup_menu()

    def setup_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

    def show_repl_tab(self):
        self.notebook.select(0)

    def show_editor_tab(self):
        self.notebook.select(1)

    def apply_theme(self):
        colors = self.custom_colors
        
        # Configure styles
        self.style.configure('.', 
                           background=colors['bg'], 
                           foreground=colors['fg'])
        self.style.configure('TButton',
                           background=colors['button_bg'],
                           foreground=colors['button_fg'],
                           borderwidth=1,
                           padding=5)
        self.style.map('TButton',
                      background=[('active', colors['select_bg']),
                                  ('disabled', colors['bg'])])
        self.style.configure('TEntry',
                           fieldbackground=colors['text_bg'],
                           foreground=colors['text_fg'],
                           insertcolor=colors['text_fg'])
        self.style.configure('Treeview',
                           background=colors['tree_bg'],
                           foreground=colors['tree_fg'],
                           fieldbackground=colors['tree_bg'])
        self.style.configure('Treeview.Heading',
                           background=colors['tree_heading_bg'],
                           foreground=colors['fg'])
        
        # Update all widgets
        self.root.config(bg=colors['bg'])
        self.update_ui_colors()

    def update_ui_colors(self):
        colors = self.custom_colors
        # Update text widgets
        for widget in [self.output_text, self.details_text, self.editor_text, self.editor_output]:
            widget.config(
                bg=colors['text_bg' if widget == self.editor_text else 'output_bg'],
                fg=colors['text_fg' if widget == self.editor_text else 'output_fg'],
                insertbackground=colors['text_fg']
            )
        
        # Update syntax highlighting
        self.editor_text.tag_configure('command', background=colors['syntax_command'])
        self.highlight_commands()
        
        # Update treeview
        self.tables_tree.config(style="Treeview")

    def setup_repl_tab(self):
        self.repl_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.repl_tab, text="REPL Mode")
        
        # Main content area
        main_frame = ttk.Frame(self.repl_tab)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Output console (left side)
        self.output_text = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, font=font.Font(family="Consolas", size=11),
            bg=self.custom_colors['text_bg'], fg=self.custom_colors['text_fg']
        )
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.output_text.config(state=tk.DISABLED)
        
        # Right panel (treeview and details)
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(0,10), pady=10)
        
        # Tables treeview
        self.tables_tree = ttk.Treeview(right_panel, show='tree', selectmode='browse')
        self.tables_tree.pack(fill=tk.BOTH, expand=True)
        self.tables_tree.heading('#0', text='Tables')
        
        # Table details
        self.details_text = scrolledtext.ScrolledText(
            right_panel, wrap=tk.WORD, font=font.Font(family="Consolas", size=9),
            height=10, bg=self.custom_colors['output_bg'], fg=self.custom_colors['output_fg']
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        self.details_text.config(state=tk.DISABLED)
        
        # Input area (bottom panel)
        input_frame = ttk.Frame(self.repl_tab)
        input_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        
        self.input_entry = ttk.Entry(input_frame, font=font.Font(family="Consolas", size=12))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.execute_repl_command)
        self.input_entry.bind("<Up>", self.history_navigation)
        self.input_entry.bind("<Down>", self.history_navigation)
        
        ttk.Button(input_frame, text="Run", command=self.execute_repl_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Clear", command=self.clear_repl_output).pack(side=tk.LEFT)

    def setup_editor_tab(self):
        self.editor_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.editor_tab, text="Editor Mode")
        
        # Editor with syntax highlighting
        self.editor_text = scrolledtext.ScrolledText(
            self.editor_tab, wrap=tk.WORD, font=font.Font(family="Consolas", size=12),
            bg=self.custom_colors['text_bg'], fg=self.custom_colors['text_fg']
        )
        self.editor_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.editor_text.tag_configure('command', background=self.custom_colors['syntax_command'])
        self.editor_text.bind('<KeyRelease>', self.highlight_commands)
        
        # Toolbar
        toolbar = ttk.Frame(self.editor_tab)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="New", command=self.new_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Open", command=self.open_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save", command=self.save_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save As", command=self.save_file_as).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Run", command=self.execute_editor).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clear", command=self.clear_editor_output).pack(side=tk.LEFT)
        
        # Output panel
        self.editor_output = scrolledtext.ScrolledText(
            self.editor_tab, wrap=tk.WORD, font=font.Font(family="Consolas", size=11),
            height=10, bg=self.custom_colors['output_bg'], fg=self.custom_colors['output_fg']
        )
        self.editor_output.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0,10))
        self.editor_output.config(state=tk.DISABLED)
        self.editor_text.bind("<Control-Return>", lambda e: self.execute_editor())

    def highlight_commands(self, event=None):
        """Syntax highlighting for Tabulae commands"""
        keywords = ['maketable', 'editrow', 'editcell', 'print', 'exportcsv', 'importcsv', 'runfile', 'query']
        
        self.editor_text.tag_remove('command', '1.0', tk.END)
        
        text = self.editor_text.get('1.0', tk.END)
        for word in keywords:
            start = '1.0'
            while True:
                start = self.editor_text.search(r'\m{}\M'.format(word), start, tk.END, 
                                               regexp=True, nocase=True)
                if not start:
                    break
                end = f"{start}+{len(word)}c"
                self.editor_text.tag_add('command', start, end)
                start = end

    def execute_repl_command(self, event=None):
        cmd = self.input_entry.get().strip()
        if not cmd:
            return
        
        self.input_entry.delete(0, tk.END)
        self.command_history.append(cmd)
        self.history_index = len(self.command_history)
        
        try:
            with io.StringIO() as buf, redirect_stdout(buf):
                self.repl_interpreter.run(cmd)
                output = buf.getvalue() or f"Executed: {cmd}"
            self.display_output(self.output_text, f">>> {cmd}\n{output}\n")
        except Exception as e:
            self.display_output(self.output_text, f">>> {cmd}\nError: {str(e)}\n")
        
        self.update_table_view()

    def execute_editor(self):
        # Clear editor output before execution
        self.clear_editor_output()
        
        code = self.editor_text.get("1.0", tk.END).strip()
        if not code:
            return
        
        output_buffer = io.StringIO()
        try:
            with redirect_stdout(output_buffer):
                self.editor_interpreter.run(code)
            output = output_buffer.getvalue()
            if not output:
                output = "Script executed successfully"
            self.display_editor_output(output)
        except Exception as e:
            self.display_editor_output(f"Error: {str(e)}")
        finally:
            output_buffer.close()

    def display_output(self, widget, text):
        widget.config(state=tk.NORMAL)
        widget.insert(tk.END, text)
        widget.see(tk.END)
        widget.config(state=tk.DISABLED)

    def update_table_view(self):
        self.tables_tree.delete(*self.tables_tree.get_children())
        for table, data in self.repl_interpreter.vars.items():
            if isinstance(data, dict) and 'columns' in data:
                parent = self.tables_tree.insert('', 'end', text=table, values=('table',))
                for col in data['columns']:
                    self.tables_tree.insert(parent, 'end', text=col, values=('column',))

    def history_navigation(self, event):
        if not self.command_history:
            return
        
        if event.keysym == "Up" and self.history_index > 0:
            self.history_index -= 1
        elif event.keysym == "Down" and self.history_index < len(self.command_history)-1:
            self.history_index += 1
        
        if 0 <= self.history_index < len(self.command_history):
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, self.command_history[self.history_index])

    def new_file(self):
        if self.check_unsaved_changes():
            self.editor_text.delete("1.0", tk.END)
            self.current_file = None
            self.clear_editor_output()

    def open_file(self):
        if not self.check_unsaved_changes():
            return
        
        path = filedialog.askopenfilename(filetypes=[("Tabulae Files", "*.tadb")])
        if path:
            try:
                with open(path, 'r') as f:
                    self.editor_text.delete("1.0", tk.END)
                    self.editor_text.insert(tk.END, f.read())
                self.current_file = path
                self.display_output(self.editor_output, f"Loaded: {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")

    def save_file(self):
        if self.current_file:
            self._save_content(self.current_file)
        else:
            self.save_file_as()

    def save_file_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".tadb",
            filetypes=[("Tabulae Files", "*.tadb")]
        )
        if path:
            self._save_content(path)
            self.current_file = path

    def _save_content(self, path):
        try:
            with open(path, 'w') as f:
                f.write(self.editor_text.get("1.0", tk.END))
            self.display_output(self.editor_output, f"Saved to: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")

    def check_unsaved_changes(self):
        if self.editor_text.edit_modified():
            return messagebox.askyesno(
                "Unsaved Changes",
                "You have unsaved changes. Discard them?",
                parent=self.root
            )
        return True

    def clear_repl_output(self):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)

    def clear_editor_output(self):
        self.editor_output.config(state=tk.NORMAL)
        self.editor_output.delete("1.0", tk.END)
        self.editor_output.config(state=tk.DISABLED)
    def execute_editor(self):
        self.clear_editor_output()  # Clear output first
        code = self.editor_text.get("1.0", tk.END).strip()
        
        if not code:
            return
        
        output_buffer = io.StringIO()
        try:
            with redirect_stdout(output_buffer):
                self.editor_interpreter.run(code)
            output = output_buffer.getvalue()
            if not output:
                output = "Script executed successfully"
            # Use correct output widget reference
            self.display_output(self.editor_output, output)
        except Exception as e:
            # Use correct error display method
            self.display_output(self.editor_output, f"Error: {str(e)}")
        finally:
            output_buffer.close()

def display_output(self, widget, text):
    widget.config(state=tk.NORMAL)
    widget.delete(1.0, tk.END)  # Clear before inserting new content
    widget.insert(tk.END, text)
    widget.config(state=tk.DISABLED)
    widget.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = TabulaeGUI(root)
    root.mainloop()
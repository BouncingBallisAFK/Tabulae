#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, font, filedialog, messagebox
from tabulae import Interpreter
import io
from contextlib import redirect_stdout

class TabulaeGUI:
    def __init__(self, root):
        self.root = root
        self.interpreter = Interpreter()
        self.command_history = []
        self.history_index = -1
        self.current_file = None
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("Tabulae GUI")
        self.root.geometry("1200x800")
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", padding=5)
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        
        # Create notebook for modes
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # REPL Mode Tab
        self.setup_repl_tab()
        
        # Editor Mode Tab
        self.setup_editor_tab()
        
    def setup_repl_tab(self):
        repl_frame = ttk.Frame(self.notebook)
        self.notebook.add(repl_frame, text="REPL Mode")
        
        # Main container
        main_frame = ttk.Frame(repl_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Output panel
        self.output_text = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            font=font.Font(family="Consolas", size=11),
            bg="#ffffff",
            padx=10,
            pady=10
        )
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.output_text.configure(state=tk.DISABLED)
        
        # Right sidebar
        sidebar_frame = ttk.Frame(main_frame)
        sidebar_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10,0))
        
        # Tables treeview
        self.tables_tree = ttk.Treeview(
            sidebar_frame,
            columns=('type',),
            show='tree',
            selectmode='browse'
        )
        self.tables_tree.heading('#0', text='Tables', anchor=tk.W)
        self.tables_tree.column('#0', width=200)
        self.tables_tree.pack(fill=tk.BOTH, expand=True)
        
        # Table details
        self.details_text = scrolledtext.ScrolledText(
            sidebar_frame,
            wrap=tk.WORD,
            font=font.Font(family="Consolas", size=9),
            height=10,
            bg="#f8f8f8"
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        self.details_text.configure(state=tk.DISABLED)
        
        # Input area
        input_frame = ttk.Frame(repl_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        
        self.input_entry = ttk.Entry(
            input_frame,
            font=font.Font(family="Consolas", size=12)
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.execute_repl_command)
        self.input_entry.bind("<Up>", self.navigate_history)
        self.input_entry.bind("<Down>", self.navigate_history)
        
        ttk.Button(
            input_frame,
            text="Run",
            command=self.execute_repl_command
        ).pack(side=tk.LEFT, padx=(5,0))
        
        ttk.Button(
            input_frame,
            text="Save",
            command=self.save_repl_history
        ).pack(side=tk.LEFT, padx=(5,0))
        
        ttk.Button(
            input_frame,
            text="Clear",
            command=self.clear_repl_output
        ).pack(side=tk.LEFT, padx=(5,0))
        
        self.update_tables_display()
        
    def setup_editor_tab(self):
        editor_frame = ttk.Frame(self.notebook)
        self.notebook.add(editor_frame, text="Editor Mode")
        
        # Button toolbar
        toolbar_frame = ttk.Frame(editor_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=(10,0))
        
        ttk.Button(
            toolbar_frame,
            text="New",
            command=self.new_file
        ).pack(side=tk.LEFT, padx=(0,5))
        
        ttk.Button(
            toolbar_frame,
            text="Open",
            command=self.open_file
        ).pack(side=tk.LEFT, padx=(0,5))
        
        ttk.Button(
            toolbar_frame,
            text="Save",
            command=self.save_file
        ).pack(side=tk.LEFT, padx=(0,5))
        
        ttk.Button(
            toolbar_frame,
            text="Save As",
            command=self.save_file_as
        ).pack(side=tk.LEFT, padx=(0,5))
        
        ttk.Button(
            toolbar_frame,
            text="Run",
            command=self.execute_editor
        ).pack(side=tk.LEFT, padx=(0,5))
        
        ttk.Button(
            toolbar_frame,
            text="Clear",
            command=self.clear_editor_output
        ).pack(side=tk.LEFT)
        
        # Editor panel
        self.editor_text = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            font=font.Font(family="Consolas", size=12),
            bg="#ffffff",
            padx=10,
            pady=10
        )
        self.editor_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Output panel
        self.editor_output = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            font=font.Font(family="Consolas", size=11),
            bg="#f8f8f8",
            height=10
        )
        self.editor_output.pack(fill=tk.BOTH, expand=False, padx=10, pady=(0,10))
        self.editor_output.configure(state=tk.DISABLED)
        
    def execute_repl_command(self, event=None):
        command = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)
        
        if not command:
            return
        
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        output_buffer = io.StringIO()
        try:
            with redirect_stdout(output_buffer):
                self.interpreter.run(command)
            output = output_buffer.getvalue()
            if not output:
                output = f"Command executed: {command}"
            self.display_repl_output(command, output)
        except Exception as e:
            self.display_repl_output(command, f"Error: {str(e)}")
        finally:
            output_buffer.close()
        
        self.update_tables_display()
    
    def execute_editor(self):
        code = self.editor_text.get("1.0", tk.END).strip()
        if not code:
            return
        
        output_buffer = io.StringIO()
        try:
            with redirect_stdout(output_buffer):
                self.interpreter.run(code)
            output = output_buffer.getvalue()
            if not output:
                output = "Script executed successfully"
            self.display_editor_output(output)
        except Exception as e:
            self.display_editor_output(f"Error: {str(e)}")
        finally:
            output_buffer.close()
        
        self.update_tables_display()
    
    def display_repl_output(self, command, result):
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, f">>> {command}\n")
        self.output_text.insert(tk.END, f"{result}\n\n")
        self.output_text.configure(state=tk.DISABLED)
        self.output_text.see(tk.END)
    
    def display_editor_output(self, result):
        self.editor_output.configure(state=tk.NORMAL)
        self.editor_output.delete(1.0, tk.END)
        self.editor_output.insert(tk.END, result)
        self.editor_output.configure(state=tk.DISABLED)
        self.editor_output.see(tk.END)
    
    def update_tables_display(self):
        for item in self.tables_tree.get_children():
            self.tables_tree.delete(item)
        
        for table_name, table_data in self.interpreter.vars.items():
            if isinstance(table_data, dict) and 'columns' in table_data:
                table_id = self.tables_tree.insert('', 'end', text=table_name, values=('table',))
                for col in table_data['columns']:
                    self.tables_tree.insert(table_id, 'end', text=col, values=('column',))
        
        self.tables_tree.bind('<<TreeviewSelect>>', self.show_table_details)
    
    def show_table_details(self, event):
        self.details_text.configure(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        selected = self.tables_tree.selection()
        if not selected:
            return
        
        item = self.tables_tree.item(selected[0])
        parent_item = self.tables_tree.parent(selected[0])
        
        if item['values'][0] == 'column':
            table_name = self.tables_tree.item(parent_item)['text']
            column_name = item['text']
            table_data = self.interpreter.vars.get(table_name)
            
            if table_data and isinstance(table_data, dict):
                columns = table_data.get('columns', [])
                data = table_data.get('data', [])
                
                if column_name in columns:
                    col_index = columns.index(column_name)
                    self.details_text.insert(tk.END,
                        f"Column: {column_name}\n"
                        f"Table: {table_name}\n"
                        f"Total Rows: {len(data)}\n\n"
                        "Values:\n"
                    )
                    
                    for row in data:
                        if len(row) > col_index:
                            row_id = row[0]
                            value = row[col_index]
                            self.details_text.insert(tk.END, f"Row {row_id}: {value}\n")
                    if not data:
                        self.details_text.insert(tk.END, "No data available")
        
        elif item['values'][0] == 'table':
            table_name = item['text']
            table_data = self.interpreter.vars.get(table_name)
            
            if table_data and isinstance(table_data, dict):
                columns = table_data.get('columns', [])
                row_count = len(table_data.get('data', []))
                
                self.details_text.insert(tk.END,
                    f"Table: {table_name}\n"
                    f"Columns: {len(columns)}\n"
                    f"Rows: {row_count}\n\n"
                    f"Columns:\n- " + "\n- ".join(columns)
                )
        
        self.details_text.configure(state=tk.DISABLED)
    
    def navigate_history(self, event):
        if self.command_history:
            if event.keysym == "Up" and self.history_index > 0:
                self.history_index -= 1
            elif event.keysym == "Down" and self.history_index < len(self.command_history)-1:
                self.history_index += 1
            
            if 0 <= self.history_index < len(self.command_history):
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, self.command_history[self.history_index])
    
    def save_repl_history(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".tadb",
            filetypes=[("Tabulae Files", "*.tadb"), ("All Files", "*.*")],
            title="Save REPL History"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    for cmd in self.command_history:
                        f.write(f"{cmd}\n")
                self.display_repl_output("[System]", f"Saved {len(self.command_history)} commands to {file_path}")
            except Exception as e:
                self.display_repl_output("[Error]", f"Failed to save: {str(e)}")
    
    def new_file(self):
        if self.current_file or self.editor_text.get("1.0", tk.END).strip():
            if not messagebox.askyesno("New File", "Unsaved changes will be lost. Continue?"):
                return
        self.editor_text.delete("1.0", tk.END)
        self.current_file = None
        self.clear_editor_output()
    
    def open_file(self):
        if self.current_file or self.editor_text.get("1.0", tk.END).strip():
            if not messagebox.askyesno("Open File", "Unsaved changes will be lost. Continue?"):
                return
        
        file_path = filedialog.askopenfilename(
            filetypes=[("Tabulae Files", "*.tadb"), ("All Files", "*.*")],
            title="Open Tabulae Script"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                self.editor_text.delete("1.0", tk.END)
                self.editor_text.insert(tk.END, content)
                self.current_file = file_path
                self.display_editor_output(f"Loaded {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def save_file(self):
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".tadb",
            filetypes=[("Tabulae Files", "*.tadb"), ("All Files", "*.*")],
            title="Save Tabulae Script"
        )
        
        if file_path:
            self._save_to_file(file_path)
            self.current_file = file_path
    
    def _save_to_file(self, file_path):
        try:
            content = self.editor_text.get("1.0", tk.END)
            with open(file_path, 'w') as f:
                f.write(content)
            self.display_editor_output(f"Saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def clear_repl_output(self):
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.configure(state=tk.DISABLED)
    
    def clear_editor_output(self):
        self.editor_output.configure(state=tk.NORMAL)
        self.editor_output.delete(1.0, tk.END)
        self.editor_output.configure(state=tk.DISABLED)

def main():
    root = tk.Tk()
    gui = TabulaeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
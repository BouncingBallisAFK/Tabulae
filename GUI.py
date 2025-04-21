#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, scrolledtext, font
from tabulae import Interpreter

class TabulaeGUI:
    def __init__(self, root):
        self.root = root
        self.interpreter = Interpreter()
        self.command_history = []
        self.history_index = -1
        self.setup_ui()
        
    def setup_ui(self):
        self.root.title("Tabulae GUI")
        self.root.geometry("1000x600")
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", padding=5)
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        
        # Create main container
        main_frame = ttk.Frame(self.root)
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
        
        # Tables panel
        tables_frame = ttk.Frame(main_frame)
        tables_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10,0))
        
        self.tables_tree = ttk.Treeview(
            tables_frame,
            columns=('type',),
            show='tree',
            selectmode='browse'
        )
        self.tables_tree.heading('#0', text='Tables', anchor=tk.W)
        self.tables_tree.column('#0', width=200)
        self.tables_tree.pack(fill=tk.BOTH, expand=True)
        
        # Table details panel
        self.details_text = scrolledtext.ScrolledText(
            tables_frame,
            wrap=tk.WORD,
            font=font.Font(family="Consolas", size=9),
            height=10,
            bg="#f8f8f8"
        )
        self.details_text.pack(fill=tk.BOTH, expand=True)
        self.details_text.configure(state=tk.DISABLED)
        
        # Input area
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        
        self.input_entry = ttk.Entry(
            input_frame,
            font=font.Font(family="Consolas", size=12)
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind("<Return>", self.execute_command)
        self.input_entry.bind("<Up>", self.navigate_history)
        self.input_entry.bind("<Down>", self.navigate_history)
        
        ttk.Button(
            input_frame,
            text="Run",
            command=self.execute_command
        ).pack(side=tk.LEFT, padx=(5,0))
        
        # Initial update
        self.update_tables_display()
        
    def execute_command(self, event=None):
        command = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)
        
        if not command:
            return
        
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        try:
            result = []
            
            # Capture print output
            import io
            from contextlib import redirect_stdout
            
            with io.StringIO() as buf, redirect_stdout(buf):
                self.interpreter.run(command)
                output = buf.getvalue()
            
            if output:
                result.append(output.strip())
        except Exception as e:
            result.append(f"Error: {str(e)}")
        
        self.display_output(command, '\n'.join(result))
        self.update_tables_display()
    
    def display_output(self, command, result):
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, f">>> {command}\n")
        if result:
            self.output_text.insert(tk.END, f"{result}\n\n")
        self.output_text.configure(state=tk.DISABLED)
        self.output_text.see(tk.END)
    
    def update_tables_display(self):
        # Clear existing items
        for item in self.tables_tree.get_children():
            self.tables_tree.delete(item)
        
        # Add tables and columns
        for table_name, table_data in self.interpreter.vars.items():
            if isinstance(table_data, dict) and 'columns' in table_data:
                table_id = self.tables_tree.insert(
                    '', 'end', 
                    text=table_name,
                    values=('table',)
                )
                for col in table_data['columns']:
                    self.tables_tree.insert(
                        table_id, 'end',
                        text=col,
                        values=('column',)
                    )
        
        # Set up selection binding
        self.tables_tree.bind('<<TreeviewSelect>>', self.show_table_details)
    
    def show_table_details(self, event):
        self.details_text.configure(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        
        selected = self.tables_tree.selection()
        if not selected:
            return
        
        item = self.tables_tree.item(selected[0])
        if item['values'][0] == 'table':
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

def main():
    root = tk.Tk()
    gui = TabulaeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
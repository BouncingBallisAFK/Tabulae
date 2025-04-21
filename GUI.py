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
        self.root.geometry("800x600")
        
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", padding=5)
        
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
        
        # History panel
        history_frame = ttk.Frame(main_frame)
        history_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_list = tk.Listbox(
            history_frame,
            width=30,
            font=font.Font(family="Consolas", size=10)
        )
        self.history_list.pack(fill=tk.Y, expand=True)
        
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
        
    def execute_command(self, event=None):
        command = self.input_entry.get().strip()
        self.input_entry.delete(0, tk.END)
        
        if not command:
            return
        
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        self.update_history_list()
        
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
    
    def display_output(self, command, result):
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.insert(tk.END, f">>> {command}\n")
        if result:
            self.output_text.insert(tk.END, f"{result}\n\n")
        self.output_text.configure(state=tk.DISABLED)
        self.output_text.see(tk.END)
    
    def update_history_list(self):
        self.history_list.delete(0, tk.END)
        for cmd in self.command_history[-10:]:  # Show last 10 commands
            self.history_list.insert(tk.END, cmd)
    
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
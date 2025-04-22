# Tabulae

**A Domain-Specific Language for Table Manipulation with Dual-Mode GUI**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)


## Features

### Core Language
- 🗃️ **Table Management**: Create tables with custom columns
- ✏️ **Data Editing**: Modify rows or individual cells
- 🔍 **Query System**: Filter data with comparison operators
- 📁 **File Integration**: Import/export CSV files

### Dual-Mode GUI
- 🖥️ **REPL Mode**: Interactive command execution
- ✍️ **Editor Mode**: Full-featured script editor
- 📊 **Table Viewer**: Visualize all tables and column data
- 🔄 **Real-time Updates**: Changes reflect immediately

### File Operations
- 💾 Save REPL history or editor content
- 📂 Open existing scripts
- ⚡ Run entire scripts with one click

## Installation

```bash
# Clone repository
git clone https://github.com/BouncingBallIsAFK/tabulae.git
cd tabulae

# Install dependencies (only tkinter needed)
sudo apt-get install python3-tk  # For Debian/Ubuntu

# Run GUI
python3 GUI.py
# Tabulae

**A Domain-Specific Language for Table Manipulation**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Tabulae is a simple yet powerful domain-specific language (DSL) designed for creating and manipulating tabular data. With features inspired by both SQL and spreadsheet operations, it offers an intuitive way to work with tables directly from your terminal or through script files.

## Features

- 🗃️ **Table Management**: Create tables with custom columns
- ✏️ **Row/Cell Editing**: Modify entire rows or individual cells
- 🔍 **Query System**: Filter data using comparison operators
- 📁 **File Integration**: Import/export CSV files and execute scripts
- 🔄 **REPL Mode**: Interactive environment for quick operations
- 🛡️ **Safety**: Strict syntax checking and error handling

## Installation

Tabulae requires Python 3.6+:

```bash
# Clone repository
git clone https://github.com/BouncingBallisAFK/Tabulae
cd tabulae

# Run directly
python3 tabulae.py [script.tadb]
```

## Quick Start

### REPL Mode

```python
>>> maketable users [id, name, age]
>>> editrow users [1, "Alice", 30]
>>> query users age > 25
| id | name  | age |
| 1  | Alice | 30  |
```

### Script Example (`demo.tadb`)

```python
importcsv "data.csv" as products
editcell products ["price", 101, 24.99]
exportcsv products "updated.csv"
```

## Command Reference

### Table Operations


| Command     | Syntax                                     | Description          |
| ------------- | -------------------------------------------- | ---------------------- |
| `maketable` | `maketable TABLENAME [COL1, COL2...]`      | Create new table     |
| `editrow`   | `editrow TABLENAME [VAL1, VAL2...]`        | Add/update row       |
| `editcell`  | `editcell TABLENAME ["COLUMN", ID, VALUE]` | Modify specific cell |

### Data Interaction


| Command | Syntax                        | Description                         |
| --------- | ------------------------------- | ------------------------------------- |
| `query` | `query TABLENAME [CONDITION]` | Print Tables and filter rows (e.g.,`salary > 50000`) |
| `print` | `print EXPRESSION`            | Display variables or calculations   |

### File Operations


| Command     | Syntax                              | Description              |
| ------------- | ------------------------------------- | -------------------------- |
| `importcsv` | `importcsv "FILE.csv" as TABLENAME` | Import CSV file          |
| `exportcsv` | `exportcsv TABLENAME "FILE.csv"`    | Export to CSV            |
| `import`    | `import "FILE.tadb"`                | Import table definitions |
| `runfile` | `runfile "SCRIPT.tadb"`           | Execute another script   |

## Examples

### Create and Modify Table

```python
maketable inventory [id, item, quantity]
editrow inventory [101, "Widget", 50]
editcell inventory ["quantity", 101, 45]
```

### Query Data

```python
query employees department == "Engineering" AND salary > 80000
```

### Import/Export Workflow

```python
importcsv "input.csv" as raw_data
editrow raw_data [..., ..., ...]
exportcsv raw_data "processed.csv"
```

## Error Handling

Tabulae provides detailed error messages with line/column numbers:

```
Error: Column 'price' not found in table 'products' 
        at line 14, column 5
```

## Limitations

- Strict syntax requirements
- All table rows must maintain consistent column count
- First column is always treated as row ID
- Imported scripts have isolated variable scope

## License

MIT License - See [LICENSE](LICENSE) for details

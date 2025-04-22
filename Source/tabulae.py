#!/usr/bin/env python3
import sys
import re
import os
import csv
from typing import List, Dict, Optional, Union

class Token:
    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

class Lexer:
    def __init__(self, code: str):
        self.code = code
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.token_specs = [
            (r'>=', 'GREATEREQUAL'),
            (r'<=', 'LESSEQUAL'),
            (r'==', 'EQUAL'),
            (r'!=', 'NOTEQUAL'),
            (r'"[^"]*"', 'STRING'),
            (r'>', 'GREATER'),
            (r'<', 'LESS'),
            (r'[ \n\t]+', None),
            (r'#[^\n]*', None),
            (r'\=', 'ASSIGN'),
            (r'\+', 'PLUS'),
            (r'\-', 'MINUS'),
            (r'\*', 'MULTIPLY'),
            (r'\/', 'DIVIDE'),
            (r'\(', 'LPAREN'),
            (r'\)', 'RPAREN'),
            (r'\[', 'LBRACKET'),
            (r'\]', 'RBRACKET'),
            (r',', 'COMMA'),
            (r'\d+', 'NUMBER'),
            (r'importcsv\b', 'IMPORT_CSV'),
            (r'import\b', 'IMPORT'),
            (r'as\b', 'AS'),
            (r'editcell\b', 'EDITCELL'),
            (r'print\b', 'PRINT'),
            (r'query\b', 'QUERY'),
            (r'maketable\b', 'MAKETABLE'),
            (r'editrow\b', 'EDITROW'),
            (r'exportcsv\b', 'EXPORTCSV'),
            (r'runfile\b', 'RUNASFILE'),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),
        ]

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.code):
            current_line = self.line
            current_column = self.column
            for pattern, tag in self.token_specs:
                regex = re.compile(pattern)
                match = regex.match(self.code, self.pos)
                if match:
                    value = match.group(0)
                    start = match.start()
                    end = match.end()
                    num_newlines = value.count('\n')
                    if num_newlines > 0:
                        self.line += num_newlines
                        last_newline_pos = value.rfind('\n')
                        chars_after = len(value) - last_newline_pos - 1
                        self.column = chars_after + 1
                    else:
                        self.column += (end - start)
                    if tag:
                        if tag == 'STRING':
                            value = value[1:-1]
                        self.tokens.append(Token(tag, value, current_line, current_column))
                    self.pos = end
                    break
            else:
                raise SyntaxError(
                    f"Unexpected character '{self.code[self.pos]}' at line {self.line}, column {self.column}"
                )
        return self.tokens

class NumberNode:
    def __init__(self, value: int):
        self.value = value

class StringNode:
    def __init__(self, value: str):
        self.value = value

class IdentifierNode:
    def __init__(self, name: str):
        self.name = name

class BinaryOpNode:
    def __init__(self, left, op: Token, right):
        self.left = left
        self.op = op
        self.right = right

class ComparisonOpNode:
    def __init__(self, left, op: Token, right):
        self.left = left
        self.op = op
        self.right = right

class AssignmentNode:
    def __init__(self, identifier: str, expr):
        self.identifier = identifier
        self.expr = expr

class PrintNode:
    def __init__(self, expr):
        self.expr = expr

class MakeTableNode:
    def __init__(self, var_name: str, columns: List[str]):
        self.var_name = var_name
        self.columns = columns

class EditRowNode:
    def __init__(self, table_name: str, values: list):
        self.table_name = table_name
        self.values = values

class EditCellNode:
    def __init__(self, table_name: str, column_expr, row_id_expr, value_expr):
        self.table_name = table_name
        self.column_expr = column_expr
        self.row_id_expr = row_id_expr
        self.value_expr = value_expr

class QueryNode:
    def __init__(self, table_name: str, condition: Optional[ComparisonOpNode]):
        self.table_name = table_name
        self.condition = condition

class ExportCSVNode:
    def __init__(self, table_name: str, filename: str):
        self.table_name = table_name
        self.filename = filename

class ImportCSVNode:
    def __init__(self, filename: str, table_name: str):
        self.filename = filename
        self.table_name = table_name

class ImportNode:
    def __init__(self, filename: str):
        self.filename = filename

class RunAsFileNode:
    def __init__(self, filename: str):
        self.filename = filename

class ProgramNode:
    def __init__(self, statements: list):
        self.statements = statements

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current_token: Optional[Token] = None
        self.next_token()

    def next_token(self):
        self.current_token = self.tokens.pop(0) if self.tokens else None

    def parse(self) -> ProgramNode:
        return self.parse_program()

    def parse_program(self) -> ProgramNode:
        statements = []
        while self.current_token:
            statements.append(self.parse_statement())
        return ProgramNode(statements)

    def parse_statement(self):
        if self.current_token.type == 'PRINT':
            return self.parse_print()
        elif self.current_token.type == 'MAKETABLE':
            return self.parse_maketable()
        elif self.current_token.type == 'EDITROW':
            return self.parse_editrow()
        elif self.current_token.type == 'EDITCELL':
            return self.parse_editcell()
        elif self.current_token.type == 'QUERY':
            return self.parse_query()
        elif self.current_token.type == 'EXPORTCSV':
            return self.parse_exportcsv()
        elif self.current_token.type == 'IMPORT_CSV':
            return self.parse_importcsv()
        elif self.current_token.type == 'IMPORT':
            return self.parse_import()
        elif self.current_token.type == 'RUNASFILE':
            return self.parse_runasfile()
        else:
            return self.parse_assignment()

    def parse_print(self) -> PrintNode:
        self.next_token()
        expr = self.parse_expression()
        return PrintNode(expr)

    def parse_maketable(self) -> MakeTableNode:
        self.next_token()
        if self.current_token.type != 'IDENTIFIER':
            raise SyntaxError(f"Expected identifier after 'maketable' at line {self.current_token.line}, column {self.current_token.column}")
        var_name = self.current_token.value
        self.next_token()
        if self.current_token.type != 'LBRACKET':
            raise SyntaxError(f"Expected '[' after table name at line {self.current_token.line}, column {self.current_token.column}")
        self.next_token()
        columns = []
        while self.current_token and self.current_token.type != 'RBRACKET':
            if self.current_token.type == 'IDENTIFIER':
                columns.append(self.current_token.value)
                self.next_token()
                if self.current_token and self.current_token.type == 'COMMA':
                    self.next_token()
            else:
                raise SyntaxError(f"Expected column name identifier at line {self.current_token.line}, column {self.current_token.column}")
        if self.current_token.type != 'RBRACKET':
            raise SyntaxError(f"Expected ']' to close column list at line {self.current_token.line}, column {self.current_token.column}")
        self.next_token()
        return MakeTableNode(var_name, columns)

    def parse_editrow(self) -> EditRowNode:
        self.next_token()
        if self.current_token.type != 'IDENTIFIER':
            raise SyntaxError(f"Expected table name after 'editrow' at line {self.current_token.line}, column {self.current_token.column}")
        table_name = self.current_token.value
        self.next_token()
        if self.current_token.type != 'LBRACKET':
            raise SyntaxError(f"Expected '[' after table name in editrow at line {self.current_token.line}, column {self.current_token.column}")
        self.next_token()
        values = []
        while self.current_token and self.current_token.type != 'RBRACKET':
            values.append(self.parse_expression())
            if self.current_token and self.current_token.type == 'COMMA':
                self.next_token()
        if self.current_token.type != 'RBRACKET':
            raise SyntaxError(f"Expected ']' to close values list in editrow at line {self.current_token.line}, column {self.current_token.column}")
        self.next_token()
        return EditRowNode(table_name, values)

    def parse_editcell(self) -> EditCellNode:
        self.next_token()
        if self.current_token.type != 'IDENTIFIER':
            raise SyntaxError(f"Expected table name after 'editcell' at line {self.current_token.line}, column {self.current_token.column}")
        table_name = self.current_token.value
        self.next_token()
        
        if self.current_token.type != 'LBRACKET':
            raise SyntaxError(f"Expected '[' after table name in editcell at line {self.current_token.line}, column {self.current_token.column}")
        self.next_token()
        
        exprs = []
        while self.current_token and self.current_token.type != 'RBRACKET' and len(exprs) < 3:
            exprs.append(self.parse_expression())
            if self.current_token and self.current_token.type == 'COMMA':
                self.next_token()
        
        if len(exprs) != 3:
            raise SyntaxError(f"Expected exactly 3 arguments in editcell at line {self.current_token.line}, column {self.current_token.column}")
        
        if self.current_token.type != 'RBRACKET':
            raise SyntaxError(f"Expected ']' to close editcell arguments at line {self.current_token.line}, column {self.current_token.column}")
        self.next_token()
        
        return EditCellNode(table_name, exprs[0], exprs[1], exprs[2])

    def parse_query(self) -> QueryNode:
        self.next_token()
        if self.current_token.type != 'IDENTIFIER':
            raise SyntaxError(f"Expected table name after 'query' at line {self.current_token.line}, column {self.current_token.column}")
        table_name = self.current_token.value
        self.next_token()
        condition = None
        if self.current_token is not None:
            condition = self.parse_comparison()
        return QueryNode(table_name, condition)

    def parse_exportcsv(self) -> ExportCSVNode:
        self.next_token()
        if self.current_token.type != 'IDENTIFIER':
            raise SyntaxError(f"Expected table name after 'exportcsv' at line {self.current_token.line}, column {self.current_token.column}")
        table_name = self.current_token.value
        self.next_token()
        if self.current_token.type != 'STRING':
            raise SyntaxError(f"Expected filename string after table name at line {self.current_token.line}, column {self.current_token.column}")
        filename = self.current_token.value
        self.next_token()
        return ExportCSVNode(table_name, filename)

    def parse_importcsv(self) -> ImportCSVNode:
        self.next_token()
        if self.current_token.type != 'STRING':
            raise SyntaxError(f"Expected filename string after 'importcsv' at line {self.current_token.line}, column {self.current_token.column}")
        filename = self.current_token.value
        self.next_token()
        if self.current_token.type != 'AS':
            raise SyntaxError(f"Expected 'as' after filename in importcsv at line {self.current_token.line}, column {self.current_token.column}")
        self.next_token()
        if self.current_token.type != 'IDENTIFIER':
            raise SyntaxError(f"Expected table name identifier after 'as' at line {self.current_token.line}, column {self.current_token.column}")
        table_name = self.current_token.value
        self.next_token()
        return ImportCSVNode(filename, table_name)

    def parse_import(self) -> ImportNode:
        self.next_token()
        if self.current_token.type != 'STRING':
            raise SyntaxError(f"Expected filename string after 'import' at line {self.current_token.line}, column {self.current_token.column}")
        filename = self.current_token.value
        self.next_token()
        return ImportNode(filename)

    def parse_runasfile(self) -> RunAsFileNode:
        self.next_token()
        if self.current_token.type != 'STRING':
            raise SyntaxError(f"Expected filename string after RUNASFILE at line {self.current_token.line}, column {self.current_token.column}")
        filename = self.current_token.value
        self.next_token()
        return RunAsFileNode(filename)

    def parse_comparison(self) -> ComparisonOpNode:
        left = self.parse_expression()
        op = self.current_token
        valid_ops = ['GREATER', 'LESS', 'EQUAL', 'NOTEQUAL', 'GREATEREQUAL', 'LESSEQUAL']
        if op.type not in valid_ops:
            raise SyntaxError(f"Expected comparison operator, got {op.type} at line {op.line}, column {op.column}")
        self.next_token()
        right = self.parse_expression()
        return ComparisonOpNode(left, op, right)

    def parse_assignment(self) -> AssignmentNode:
        identifier_token = self.current_token
        identifier = identifier_token.value
        self.next_token()
        if not self.current_token or self.current_token.type != 'ASSIGN':
            if self.current_token:
                error_msg = f"Expected '=' after identifier '{identifier}' at line {self.current_token.line}, column {self.current_token.column}"
            else:
                error_msg = f"Expected '=' after identifier '{identifier}' but reached end of input"
            raise SyntaxError(error_msg)
        self.next_token()
        expr = self.parse_expression()
        return AssignmentNode(identifier, expr)

    def parse_expression(self):
        node = self.parse_term()
        while self.current_token and self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token
            self.next_token()
            node = BinaryOpNode(node, op, self.parse_term())
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token and self.current_token.type in ('MULTIPLY', 'DIVIDE'):
            op = self.current_token
            self.next_token()
            node = BinaryOpNode(node, op, self.parse_factor())
        return node

    def parse_factor(self):
        token = self.current_token
        if token.type == 'NUMBER':
            self.next_token()
            return NumberNode(int(token.value))
        elif token.type == 'STRING':
            self.next_token()
            return StringNode(token.value)
        elif token.type == 'IDENTIFIER':
            self.next_token()
            return IdentifierNode(token.value)
        elif token.type == 'LPAREN':
            self.next_token()
            node = self.parse_expression()
            if self.current_token.type != 'RPAREN':
                raise SyntaxError(f"Expected ')' at line {self.current_token.line}, column {self.current_token.column}")
            self.next_token()
            return node
        else:
            raise SyntaxError(f"Unexpected token: {token.type} at line {token.line}, column {token.column}")

class Interpreter:
    def __init__(self):
        self.vars: Dict[str, dict] = {}
        self.should_exit = False
        self.current_file: str = "<interactive>"
        self.call_stack: List[str] = []

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node):
        raise Exception(f"No visit method for {type(node).__name__}")

    def visit_NumberNode(self, node: NumberNode) -> int:
        return node.value

    def visit_StringNode(self, node: StringNode) -> str:
        return node.value

    def visit_IdentifierNode(self, node: IdentifierNode):
        return self.vars.get(node.name)

    def visit_BinaryOpNode(self, node: BinaryOpNode):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op.type == 'PLUS':
            return left + right
        elif node.op.type == 'MINUS':
            return left - right
        elif node.op.type == 'MULTIPLY':
            return left * right
        elif node.op.type == 'DIVIDE':
            return left // right

    def visit_ComparisonOpNode(self, node: ComparisonOpNode) -> bool:
        left = self.visit(node.left)
        right = self.visit(node.right)
        match node.op.type:
            case 'GREATER': return left > right
            case 'LESS': return left < right
            case 'EQUAL': return left == right
            case 'NOTEQUAL': return left != right
            case 'GREATEREQUAL': return left >= right
            case 'LESSEQUAL': return left <= right

    def visit_AssignmentNode(self, node: AssignmentNode):
        self.vars[node.identifier] = self.visit(node.expr)

    def visit_PrintNode(self, node: PrintNode):
        value = self.visit(node.expr)
        if isinstance(value, dict):
            print(f"\nTable {node.expr.name}:")
            print("Columns:", value['columns'])
            print("Rows:")
            for row in value['data']:
                print(row)
        else:
            print(value)

    def visit_MakeTableNode(self, node: MakeTableNode):
        self.vars[node.var_name] = {
            'columns': node.columns,
            'data': []
        }

    def visit_EditRowNode(self, node: EditRowNode):
        table = self.vars.get(node.table_name)
        if not table:
            raise NameError(f"Table '{node.table_name}' not found")
        
        values = [self.visit(expr) for expr in node.values]
        
        if len(values) != len(table['columns']):
            raise ValueError(f"Expected {len(table['columns'])} values, got {len(values)}")

        row_id = values[0]
        found = False
        
        for i, row in enumerate(table['data']):
            if row[0] == row_id:
                table['data'][i] = values
                found = True
                break
        
        if not found:
            table['data'].append(values)

    def visit_EditCellNode(self, node: EditCellNode):
        table = self.vars.get(node.table_name)
        if not table:
            raise NameError(f"Table '{node.table_name}' not found")
        
        column = self.visit(node.column_expr)
        row_id = self.visit(node.row_id_expr)
        new_value = self.visit(node.value_expr)
        
        if not isinstance(column, str):
            raise TypeError(f"Column name must be a string, got {type(column).__name__}")
        
        if column not in table['columns']:
            raise ValueError(f"Column '{column}' not found in table '{node.table_name}'")
        
        col_index = table['columns'].index(column)
        found = False
        
        for row in table['data']:
            if row[0] == row_id:
                row[col_index] = new_value
                found = True
                break
        
        if not found:
            raise ValueError(f"Row with ID {row_id} not found in table '{node.table_name}'")

    def visit_QueryNode(self, node: QueryNode):
        table = self.vars.get(node.table_name)
        if not table:
            raise NameError(f"Table '{node.table_name}' not found")
        
        columns = table['columns']
        results = table['data'].copy() if node.condition is None else []
        
        if node.condition is not None:
            for row in table['data']:
                context = dict(zip(columns, row))
                original_vars = self.vars.copy()
                self.vars.update(context)
                try:
                    if self.visit(node.condition):
                        results.append(row)
                finally:
                    self.vars = original_vars
        
        print(f"\nQuery results for {node.table_name}:")
        print("| "+" | ".join(columns)+" |")
        for row in results:
            print("| "+" | ".join(map(str, row))+" |")

    def visit_ExportCSVNode(self, node: ExportCSVNode):
        table = self.vars.get(node.table_name)
        if not table:
            raise NameError(f"Table '{node.table_name}' not found")
        
        try:
            with open(node.filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(table['columns'])
                writer.writerows(table['data'])
            print(f"Exported {len(table['data'])} rows to {node.filename}")
        except Exception as e:
            raise RuntimeError(f"Failed to export CSV: {str(e)}")

    def visit_ImportCSVNode(self, node: ImportCSVNode):
        try:
            with open(node.filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                columns = next(reader)
                data = []
                for row in reader:
                    converted_row = []
                    for val in row:
                        try:
                            converted_val = int(val)
                        except ValueError:
                            converted_val = val
                        converted_row.append(converted_val)
                    data.append(converted_row)
            self.vars[node.table_name] = {
                'columns': columns,
                'data': data
            }
            print(f"Imported {len(data)} rows into table '{node.table_name}'")
        except FileNotFoundError:
            raise RuntimeError(f"CSV file '{node.filename}' not found")
        except Exception as e:
            raise RuntimeError(f"Failed to import CSV: {str(e)}")

    def visit_ImportNode(self, node: ImportNode):
        filename = node.filename
        if not os.path.isabs(filename):
            if self.current_file != "<interactive>":
                filename = os.path.join(os.path.dirname(self.current_file), filename)
            
        if filename in self.call_stack:
            raise RuntimeError(f"Circular import detected: {' -> '.join(self.call_stack + [filename])}")
            
        try:
            with open(filename, 'r') as f:
                code = f.read()
            
            original_call_stack = self.call_stack.copy()
            self.call_stack.append(filename)
            original_file = self.current_file
            self.current_file = filename
            
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            program = parser.parse()
            
            # Only process table creation and editing commands
            for stmt in program.statements:
                if isinstance(stmt, (MakeTableNode, EditRowNode)):
                    self.visit(stmt)
            
            self.call_stack = original_call_stack
            self.current_file = original_file
            print(f"Imported tables from '{filename}'")
        except Exception as e:
            raise RuntimeError(f"Import failed: {str(e)}")

    def visit_RunAsFileNode(self, node: RunAsFileNode):
        filename = node.filename
        if not os.path.isabs(filename):
            if self.current_file != "<interactive>":
                filename = os.path.join(os.path.dirname(self.current_file), filename)
            
        if filename in self.call_stack:
            raise RuntimeError(f"Circular execution detected: {' -> '.join(self.call_stack + [filename])}")
            
        try:
            with open(filename, 'r') as f:
                code = f.read()
            
            original_vars = self.vars.copy()
            self.call_stack.append(filename)
            prev_file = self.current_file
            self.current_file = filename
            
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            program = parser.parse()
            self.visit(program)
            
            self.vars = original_vars
            self.call_stack.pop()
            self.current_file = prev_file
            
            self.should_exit = True
            
        except Exception as e:
            raise RuntimeError(f"RUNASFILE failed: {str(e)}")

    def visit_ProgramNode(self, node: ProgramNode):
        for stmt in node.statements:
            self.visit(stmt)

    def run(self, code: str, is_file: bool = False):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        self.visit(program)

def main():
    interpreter = Interpreter()
    
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if not filename.endswith('.tadb'):
            print("Error: Tabulae files must have .tadb extension")
            return
            
        try:
            with open(filename, 'r') as f:
                code = f.read()
            interpreter.run(code, is_file=True)
            if interpreter.should_exit:
                sys.exit(0)
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    else:
        print("Tabulae REPL (type 'exit' to quit)")
        while True:
            try:
                code = input('>>> ')
                if code.strip().lower() == 'exit':
                    break
                interpreter.run(code)
                if interpreter.should_exit:
                    print("Exiting due to RUNASFILE command")
                    break
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")

if __name__ == '__main__':
    main()
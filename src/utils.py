import json
import io

from src.lexer.token import Token
from src.semantic.symbol.symbol_table import *

def read_file(path):
    '''Read pascal file (input)'''
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
def read_json(path: str):
    '''Read config (json)'''
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def format_tokens(tokens):
    '''Format tokens output berdasarkan spek'''
    return "\n".join(f"{token.type}({token.value})" for token in tokens)

def symbol_table_to_str(symbol_table):
    import sys
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        symbol_table.print_tables()  
    finally:
        sys.stdout = old_stdout
    result = buf.getvalue()
    buf.close()
    return result

def write_file(output, output_path):
    '''Write formatted token ke output path'''
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
        
def format_output(ast_root, root, tokens, dir_output, symbol_table=None):
    '''Output helper'''
    output = ""
    if int(dir_output[-1:]) == 1:
        output = format_tokens(tokens)
    elif int(dir_output[-1:]) == 2:
        output = str(root)
    elif int(dir_output[-1:]) == 3:
        output = ""
        if symbol_table: 
            output += "============================= SEMANTIC ANALYSIS + SYMBOL TABLE =============================\n\n"
            output += symbol_table + "\n"
            output += "================================= DECORATED AST =================================\n\n"
        output += str(ast_root)

    return output

def print_usage():
    '''Usage for input error'''
    print("Usage: python main.py <milestone-x/input/source_file.pas>")
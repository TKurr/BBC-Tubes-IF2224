import json
from src.lexer.token import Token

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

def write_file(output, output_path):
    '''Write formatted token ke output path'''
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
        
def format_output(ast_root, root, tokens, dir_output):
    '''Output helper'''
    output = ""
    if int(dir_output[-1:]) == 1:
        output = format_tokens(tokens)
    elif int(dir_output[-1:]) == 2:
        output = str(root)
    elif int(dir_output[-1:]) == 3:
        output = str(ast_root)
    return output

def print_usage():
    '''Usage for input error'''
    print("Usage: python main.py <milestone-x/input/source_file.pas>")
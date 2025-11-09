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

def read_txt(file_path):
    tokens = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if "(" in line and line.endswith(")"):
                token_type, token_value = line.split("(", 1)
                token_value = token_value[:-1]  
                token = Token(
                    type=token_type.strip(),
                    value=token_value.strip(),
                    line=0,
                    column=0
                )
                tokens.append(token)
    return tokens

def format_tokens(tokens):
    '''Format tokens output berdasarkan spek'''
    return "\n".join(f"{token.type}({token.value})" for token in tokens)

def write_file(output, output_path):
    '''Write formatted token ke output path'''
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
        
def format_output(root, tokens, dir_output):
    '''Output helper'''
    output = ""
    if int(dir_output[-1:]) == 1:
        output = format_tokens(tokens)
    elif int(dir_output[-1:]) == 2:
        output = str(root)
    return output

def print_usage():
    '''Usage for input error'''
    print("Usage: python main.py <milestone-x/input/source_file.pas>")
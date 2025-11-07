import json

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
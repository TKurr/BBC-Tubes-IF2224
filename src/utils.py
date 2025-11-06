import json

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
def read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def format_tokens(tokens):
    return "\n".join(f"{token.type}({token.value})" for token in tokens)

def write_file(output, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)
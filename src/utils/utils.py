def read_file(path):
    with open(path, "r") as f:
        return f.read()

def format_tokens(tokens):
    return "\n".join(str(token) for token in tokens)
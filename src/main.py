import os
import sys
from lexer.lexer import Lexer
from utils.utils import read_file
from utils.utils import format_tokens

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <source_file.pas>")
        sys.exit(1)

    source_path = sys.argv[1]
    try:
        source_code = read_file(source_path)
    except FileNotFoundError:
        print(f"[Error] File '{source_path}' not found.")
        sys.exit(1)

    lexer = Lexer(os.path.join(os.path.dirname(__file__), "config/dfa_rules.json"))
    tokens = lexer.tokenize(source_code)

    print(format_tokens(tokens))

if __name__ == "__main__":
    main()

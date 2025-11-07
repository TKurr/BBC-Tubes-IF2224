import os
import sys
from lexer.lexer import Lexer
from utils.utils import read_file, format_tokens

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
    output = format_tokens(tokens)

    # Buat direktori output jika belum ada
    output_dir = os.path.join("test", "milestone-1")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "output.txt")

    # Simpan hasil ke file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    main()

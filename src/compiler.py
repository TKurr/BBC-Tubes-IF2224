import os
import sys
from pathlib import Path
from src.lexer.lexer import Lexer
from src.dfa.dfa_engine import DFAEngine
from src.dfa.dfa_config import DFAConfigLoader
from src.lexer.lexer_config import LexerConfigLoader
from src.lexer.lexical_error import LexicalError
from src.utils import read_file, format_tokens, write_file

def compiler():
    if len(sys.argv) != 2:
        print("Usage: python main.py <source_file.pas>")
        sys.exit(1)

    try:
        # Config Path
        BASE_DIR = Path(sys.argv[0]).resolve().parent
        CONFIG_DIR = BASE_DIR / "src" / "config"
        STATE_PATH = os.path.join(CONFIG_DIR, "states.json")
        TRANSITIONS_PATH = os.path.join(CONFIG_DIR, "transitions.json")
        LEXER_CONFIG_PATH = os.path.join(CONFIG_DIR, "token_maps.json")
        
        # Load config
        dfa_config = DFAConfigLoader.load(STATE_PATH, TRANSITIONS_PATH)
        lexer_config = LexerConfigLoader.load(LEXER_CONFIG_PATH)

    except FileNotFoundError as e:
        print(f"[Config Error] Config file not found: {e.filename}")
        sys.exit(1)
    except ValueError as e:
        print(f"[Config Error] Config file failed to load: {e}")
        sys.exit(1)

	# Initialize engine & lexer
    dfa_engine = DFAEngine(dfa_config)
    lexer = Lexer(dfa_engine, lexer_config)
    
    # Input source file
    source_path = os.path.join(BASE_DIR, "test", "milestone-2", "input", sys.argv[1])
    try:
        source_code = read_file(source_path)
    except FileNotFoundError:
        print(f"[Error] File '{source_path}' not found.")
        sys.exit(1)

	# Tokenize
    try:
        tokens = lexer.tokenize(source_code)
        output = format_tokens(tokens)
    except LexicalError as e:
        print(str(e))
        sys.exit(1)
        
    #output
    lexer_relative_path = '/'.join(['test','milestone-2','output','output.txt'])
    lexer_output_path = os.path.join(BASE_DIR, lexer_relative_path)
    write_file(output,lexer_output_path)
    print(f"SAVED LEXER => {lexer_relative_path}")
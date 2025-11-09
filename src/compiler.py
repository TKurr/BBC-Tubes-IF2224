import os
import sys
from pathlib import Path
from src.lexer.lexer import Lexer
from src.dfa.dfa_engine import DFAEngine
from src.dfa.dfa_config import DFAConfigLoader
from src.lexer.lexer_config import LexerConfigLoader
from src.lexer.lexical_error import LexicalError
from src.parser.parse_error import ParseError
from src.utils import read_file, write_file, format_output, print_usage
from src.parser.parser import Parser

def compiler():
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)
    else:
        parts = sys.argv[1].replace("\\", "/").split("/")
        dir_output = parts[0]
        print(dir_output)

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
    source_path = BASE_DIR / "test" / sys.argv[1]
    try:
        source_code = read_file(source_path)
    except FileNotFoundError:
        print_usage()
        sys.exit(1)

    try:
        #Tokenize
        tokens = lexer.tokenize(source_code)
        
        #Parse Tree
        parser = Parser(tokens)
        root = parser.parse()
    except LexicalError as e:
        print(str(e))
        sys.exit(1)
    except ParseError as e:
        e.full_source_text = source_code
        print(str(e))
        sys.exit(1)
        
    #output
    output = format_output(root,tokens,dir_output)
    lexer_relative_path = '/'.join(['test',dir_output,'output','output.txt'])
    lexer_output_path = os.path.join(BASE_DIR, lexer_relative_path)
    write_file(output,lexer_output_path)
    print(f"SAVED	=>	{lexer_relative_path}")
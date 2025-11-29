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
from src.semantic.AST.ast_node import ASTNode
from src.semantic.AST.ast_builder import ASTBuilder
from src.semantic.symbol.symbol_table import SymbolTable
from src.semantic.semantic_analyzer import SemanticAnalyzer
from src.semantic.errors import SemanticError

def print_ast(node, indent=0):
    """Print plain AST without decorations"""
    prefix = "  " * indent

    if isinstance(node, ASTNode):
        print(f"{prefix}{repr(node)}")

        for child in getattr(node, 'children', []):
            print_ast(child, indent + 1)
    else:
        print(f"{prefix}{node}")

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
        # Milestone 1: read pascal -> tokenize
        if dir_output == "milestone-1" or dir_output == "milestone-2" or dir_output == "milestone-3":
            source_code = read_file(source_path)
            tokens = lexer.tokenize(source_code)
        else:
            print("[Error] Unknown directory, expected milestone-1 or milestone-2")
            sys.exit(1)
    except LexicalError as e:
        print(str(e))
        sys.exit(1)
    except FileNotFoundError:
        print_usage()
        sys.exit(1)

    try:
        # biar milestone-1 ga parse
        root = None
        if dir_output == "milestone-2" or dir_output == "milestone-3":
            parser = Parser(tokens)
            root = parser.parse()

    except ParseError as e:
        e.full_source_text = source_code
        print(str(e))
        sys.exit(1)

    try:
        ast_root = None
        if dir_output == "milestone-3":
            keywords_path = Path("src/config/token_maps.json")
            ast_builder = ASTBuilder(root)
            ast_root = ast_builder.build()

            print("\n=============== SEMANTIC ANALYSIS ===============")
            analyzer = SemanticAnalyzer()
            success, errors = analyzer.analyze(ast_root)

            analyzer.symbol_table.print_tables()

            print("\n===== DECORATED ABSTRACT SYNTAX TREE =====\n")
            print(ast_root)

            if not success:
                print("Semantic errors found:")
                for error in errors:
                    print(f"  - {error}")
                sys.exit(1)
            else:
                print("\n[OK] Semantic analysis passed!")
                print(f"[OK] Symbol table created with {len(analyzer.symbol_table.tab)} entries")

    except SemanticError as e:
        print(f"[Semantic Error] {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"[AST Builder Error] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    #output
    output = format_output(ast_root, root,tokens,dir_output)
    lexer_relative_path = '/'.join(['test',dir_output,'output','output.txt'])
    lexer_output_path = os.path.join(BASE_DIR, lexer_relative_path)
    write_file(output,lexer_output_path)
    print(f"SAVED => {lexer_relative_path}")

    # if dir_output == "milestone-3":
    #     print("\n===== ABSTRACT SYNTAX TREE OUTPUT =====\n")
    #     print(output)

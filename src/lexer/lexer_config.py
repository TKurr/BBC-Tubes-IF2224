from dataclasses import dataclass
from typing import Dict, Set
from src.utils import read_json

@dataclass(frozen=True)
class LexerConfig:
    keywords: Set[str]
    operators_map: Dict[str, str]
    state_token_map: Dict[str, str]


class LexerConfigLoader:
    @staticmethod
    def load(path: str) -> LexerConfig:
        data = read_json(path)
        
        missing = [k for k in ("keywords", "operators_map", "state_token_map") if k not in data]
        if missing:
            raise ValueError(f"Missing keys in lexer config: {', '.join(missing)}")
        
        keywords = set(data["keywords"])
        operators_map: Dict[str, str] = dict(data["operators_map"])
        state_token_map: Dict[str, str] = dict(data["state_token_map"])
        
        return LexerConfig(
            keywords=keywords,
            operators_map=operators_map,
            state_token_map=state_token_map
        )

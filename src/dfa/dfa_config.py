from dataclasses import dataclass
from typing import Dict, Set
from src.utils import read_json

StateTransitions = Dict[str,str]

@dataclass(frozen=True)
class DFAConfig:
    '''Store states & transitions dari Json config'''
    start_state: str
    final_states: Set[str]
    states: Set[str]
    transitions: Dict[str,StateTransitions]
    

class DFAConfigLoader: 
    '''DFA confiig loader'''
    @staticmethod
    def load(state_path: str, transitions_path: str) -> DFAConfig:
        state_data = read_json(state_path)
        transition_data = read_json(transitions_path)
        
        missing = [k for k in ("start_state", "final_states") if k not in state_data]
        if missing:
            raise ValueError(f"Missing keys in DFA config: {', '.join(missing)}")
        
        start_state = state_data["start_state"]
        final_states = set(state_data["final_states"])
        transitions: Dict[str, StateTransitions] = transition_data
        
        states: Set[str] = set(transitions.keys())
        for mapping in transitions.values():
            states.update(mapping.values())
        states.update(final_states)
        
        return DFAConfig(
            start_state = start_state,
            final_states = final_states,
            states = states,
            transitions = transitions
		)
     
     
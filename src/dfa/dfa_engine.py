from .dfa_config import DFAConfig

class DFAEngine:
    def __init__(self, config: DFAConfig):
        self.config = config
        self.current_state = config.start_state
        self.last_final_state = None

    def reset(self):
        self.current_state = self.config.start_state
        self.last_final_state = None

    def next_state(self, char):
        trans = self.config.transitions.get(self.current_state, {})

        if char in trans:
            self.current_state = trans[char]
        elif "<LETTER>" in trans and char.isalpha():
            self.current_state = trans["<LETTER>"]
        elif "<DIGIT>" in trans and char.isdigit():
            self.current_state = trans["<DIGIT>"]
        elif "<ANY>" in trans:
            self.current_state = trans["<ANY>"]
        else:
            return False

        if self.current_state in self.config.final_states:
            self.last_final_state = self.current_state

        return True

    def is_accepting(self):
        return self.current_state in self.config.final_states

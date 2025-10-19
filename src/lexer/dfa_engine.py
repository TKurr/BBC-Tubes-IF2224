class DFAEngine:
    def __init__(self, start_state, final_states, transitions):
        self.start_state = start_state
        self.final_states = final_states
        self.transitions = transitions
        self.current_state = start_state

    def reset(self):
        self.current_state = self.start_state

    def next_state(self, char):
        trans = self.transitions.get(self.current_state, {})
        if char in trans:
            self.current_state = trans[char]
            return True
        elif "<LETTER>" in trans and char.isalpha():
            self.current_state = trans["<LETTER>"]
            return True
        elif "<DIGIT>" in trans and char.isdigit():
            self.current_state = trans["<DIGIT>"]
            return True
        if "<ANY>" in trans:
            self.current_state = trans["<ANY>"]
            return True
        else:
            return False

    def is_accepting(self):
        return self.current_state in self.final_states

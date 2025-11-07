class DFAEngine:
    def __init__(self, start_state, final_states, transitions):
        self.start_state = start_state
        self.final_states = set(final_states)
        self.transitions = transitions
        self.current_state = start_state
        self.last_final_state = None   # <-- nambah ini

    def reset(self):
        self.current_state = self.start_state
        self.last_final_state = None   # <-- reset juga

    def next_state(self, char):
        trans = self.transitions.get(self.current_state, {})

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

        if self.current_state in self.final_states:
            self.last_final_state = self.current_state

        return True

    def is_accepting(self):
        return self.current_state in self.final_states

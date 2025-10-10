import json

class DFALoader:
    def __init__(self, path):
        self.path = path
        self.start_state = None
        self.final_states = set()
        self.transitions = {}

    def load(self):
        with open(self.path, "r") as f:
            data = json.load(f)
        self.start_state = data["start_state"]
        self.final_states = set(data["final_states"])
        self.transitions = data["transitions"]
        return self

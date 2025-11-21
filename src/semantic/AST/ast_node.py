class ASTNode:
    def __init__(self):
        self.children = []
        self.attr = {} 

    def add_child(self, child):
        self.children.append(child)

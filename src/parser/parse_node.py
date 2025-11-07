
class ParseNode:
    def __init__(self, type: str):
        self.type = type
        self.child = []

    def add_child(self, node: "ParseNode"):
        self.child.append(node)

    def __str__(self, level=0):
        result = "  " * level + f"{self.type}\n"
        for c in self.child:
            if isinstance(c, ParseNode):
                result += c.__str__(level + 1)
            else:
                result += "  " * (level + 1)
                if hasattr(c, "type") and hasattr(c, "value"):
                    result += f"{c.type}({c.value})\n"
                else:
                    result += f"{str(c)}\n"
        return result

    __repr__ = __str__


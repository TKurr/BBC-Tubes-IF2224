
class ParseNode:
    def __init__(self, type: str):
        self.type = type
        self.child = []

    def add_child(self, node: "ParseNode"):
        self.child.append(node)        
        
    def __str__(self, level=0, prefix=""):
        '''Parse Tree Output'''
        lines = []
        if level == 0:
            lines.append(f"{self.type}")
        else:
            lines.append(f"{prefix}└── {self.type}")
            
        child_count = len(self.child)
        for i, c in enumerate(self.child):
            is_last = (i == child_count - 1)
            connector = "└── " if is_last else "├── "
            next_prefix = prefix + ("    " if is_last else "│   ")
            
            if isinstance(c, ParseNode):
                lines.append(f"{prefix}{connector}{c.type}")
                child_lines = c.__str__(level + 1, next_prefix).splitlines()
                lines.extend(child_lines[1:]) 
            else:
                if hasattr(c, "type") and hasattr(c, "value"):
                    lines.append(f"{prefix}{connector}{c.type}({c.value})")
                else:
                    lines.append(f"{prefix}{connector}{str(c)}")
                    
        return "\n".join(lines)



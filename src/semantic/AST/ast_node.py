class ASTNode:
    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    # def __str__(self, level=0, prefix="", is_last=True):
    #     lines = []
    #     node_repr = repr(self)

    #     # Connector
    #     connector = "└── " if is_last else "├── "
    #     if level == 0:
    #         lines.append(node_repr)
    #     else:
    #         lines.append(f"{prefix}{connector}{node_repr}")

    #     # Prepare prefix for children
    #     if level == 0:
    #         new_prefix = ""
    #     else:
    #         new_prefix = prefix + ("    " if is_last else "│   ")

    #     # Process children
    #     child_count = len(self.children)
    #     for i, c in enumerate(self.children):
    #         last_child = (i == child_count - 1)
    #         if isinstance(c, ASTNode):
    #             lines.append(c.__str__(level + 1, new_prefix, last_child))
    #         else:
    #             # fallback for non-ASTNode children
    #             child_connector = "└── " if last_child else "├── "
    #             lines.append(f"{new_prefix}{child_connector}{str(c)}")

    #     return "\n".join(lines)
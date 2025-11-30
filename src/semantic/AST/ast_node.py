from ..symbol.constants import TypeKind
class ASTNode:
    def __init__(self):
        self.children = []
        self.attr = {}

    def add_child(self, child):
        self.children.append(child)

    def __str__(self):
        return self._format_tree("", True)

    def _format_tree(self, prefix, is_last):
        connector = "└─ " if is_last else "├─ "
        annotation = self._get_annotation_str()

        # Bersihkan repr dari newline
        node_repr = repr(self).strip()
        line = f"{prefix}{connector}{node_repr}{annotation}\n"

        child_prefix = prefix + ("   " if is_last else "│  ")
        valid_children = [c for c in self.children if c is not None]
        count = len(valid_children)

        for i, child in enumerate(valid_children):
            if hasattr(child, '_format_tree'):
                line += child._format_tree(child_prefix, i == count - 1)
            else:
                line += f"{child_prefix}{'└─ ' if i == count-1 else '├─ '}{str(child)}\n"
        return line

    def _get_annotation_str(self):
        parts = []
        type_map = {
            TypeKind.NOTYPE: "void", TypeKind.INTEGER: "integer",
            TypeKind.REAL: "real", TypeKind.BOOLEAN: "boolean",
            TypeKind.CHAR: "char", TypeKind.STRING: "string",
            TypeKind.ARRAY: "array", TypeKind.RECORD: "record",
            "predefined": "predefined"
        }

        if self.attr.get('type') == 'predefined': parts.append("predefined")

        if 'tab_index' in self.attr and self.attr['tab_index'] is not None:
            parts.append(f"tab_index:{self.attr['tab_index']}")

        if 'block_index' in self.attr:
            parts.append(f"block_index:{self.attr['block_index']}")

        if 'type' in self.attr and self.attr['type'] != 'predefined':
            val = self.attr['type']
            t_str = type_map.get(val, str(val)) if isinstance(val, int) else str(val)
            parts.append(f"type:{t_str}")

        if 'lev' in self.attr: parts.append(f"lev:{self.attr['lev']}")

        return " → " + ", ".join(parts) if parts else ""

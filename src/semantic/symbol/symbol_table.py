from typing import List, Optional, Any, Dict
from .constants import ReservedWords, ObjKind, TypeKind

class SymbolTable:
    def __init__(self):
        self.tab: List[Dict[str, Any]] = [] 
        self.btab: List[Dict[str, Any]] = []
        self.atab: List[Dict[str, Any]] = []
        self.display: List[int] = []
        self.current_level = 0

        for word in ReservedWords.LIST:
            self.tab.append({
                "name": word,
                "link": 0,
                "obj": ObjKind.RESERVED,
                "type": TypeKind.NOTYPE,
                "ref": 0,
                "nrm": 0,
                "lev": 0,
                "adr": 0
            })

        self.btab.append({
            "index": 0,
            "last": 0,
            "lpar": 0,
            "psze": 0,
            "vsze": 0
        })
        self.display = [0]

    # Inner Declaration
    def enter_scope(self):
        """Masuk procedure / function"""
        self.current_level += 1
        new_block_index = len(self.btab)

        self.btab.append({
            "index": new_block_index,
            "last": 0,
            "lpar": 0,
            "psze": 0,
            "vsze": 0
        })

        # Update Display Vector
        if len(self.display) <= self.current_level:
            self.display.append(new_block_index)
        else:
            self.display[self.current_level] = new_block_index
        return new_block_index

    def exit_scope(self):
        """Keluar procedure / function"""
        if self.current_level > 0:
            self.current_level -= 1

    # Add Entries
    def add_variable(self, name: str, type_kind: int, size: int = 1):
        """Tambah variabel lokal"""
        current_btab_idx = self.display[self.current_level]
        current_block = self.btab[current_btab_idx]

        # Linked List & addr
        link_idx = current_block["last"]
        adr = current_block["vsze"]

        new_entry = {
            "name": name,
            "link": link_idx,
            "obj": ObjKind.VARIABLE,
            "type": type_kind,
            "ref": 0,
            "nrm": 1,
            "lev": self.current_level,
            "adr": adr
        }
        self.tab.append(new_entry)

        # update block
        new_id_idx = len(self.tab) - 1
        current_block["last"] = new_id_idx
        current_block["vsze"] += size
        return new_id_idx

    def add_parameter(self, name: str, type_kind: int, is_var: bool = False):
        """Tambah parameter prosedur/fungsi"""
        current_btab_idx = self.display[self.current_level]
        current_block = self.btab[current_btab_idx]

        link_idx = current_block["last"]
        nrm_val = 0 if is_var else 1

        new_entry = {
            "name": name,
            "link": link_idx,
            "obj": ObjKind.VARIABLE,
            "type": type_kind,
            "ref": 0,
            "nrm": nrm_val,
            "lev": self.current_level,
            "adr": current_block["psze"]
        }
        self.tab.append(new_entry)

        # Update Blok (lpar & psze)
        new_id_idx = len(self.tab) - 1
        current_block["last"] = new_id_idx
        current_block["lpar"] = new_id_idx
        current_block["psze"] += 1
        return new_id_idx

    def add_program_name(self, name: str):
        """
        Khusus untuk nama program: Masukkan ke tabel tapi JANGAN update 'last'.
        Agar variabel pertama (a) nanti link-nya ke 0, bukan ke Hello.
        """
        new_entry = {
            "name": name,
            "link": 0,
            "obj": ObjKind.PROGRAM,
            "type": TypeKind.NOTYPE,
            "ref": 0,
            "nrm": 1,
            "lev": 0,
            "adr": 0
        }
        self.tab.append(new_entry)
        return len(self.tab) - 1

    def add_constant(self, name: str, type_kind: int, value: Any):
        """add Konstanta"""
        current_btab_idx = self.display[self.current_level]
        current_block = self.btab[current_btab_idx]
        link_idx = current_block["last"]

        new_entry = {
            "name": name,
            "link": link_idx,
            "obj": ObjKind.CONSTANT,
            "type": type_kind,
            "ref": 0,
            "nrm": 1,
            "lev": self.current_level,
            "adr": value
        }
        self.tab.append(new_entry)

        new_id_idx = len(self.tab) - 1
        current_block["last"] = new_id_idx
        return new_id_idx

    def add_array_info(self, xtyp: int, etyp: int, low: int, high: int, elsz: int):
        """Menambah Info Array ke ATAB"""
        size = (high - low + 1) * elsz
        entry = {
            "index": len(self.atab) + 1,
            "xtyp": xtyp,
            "etyp": etyp,
            "eref": 0,
            "low": low,
            "high": high,
            "elsz": elsz,
            "size": size
        }
        self.atab.append(entry)
        return len(self.atab) - 1

    def add_procedure(self, name: str, kind: str):
        """Tambah nama fungsi / prosedur di scope saat ini"""
        current_btab_idx = self.display[self.current_level]
        current_block = self.btab[current_btab_idx]

        link_idx = current_block["last"]

        new_entry = {
            "name": name,
            "link": link_idx,
            "obj": kind,
            "type": TypeKind.NOTYPE, # Nanti diupdate kalo functin (return type)
            "ref": 0,
            "nrm": 1,
            "lev": self.current_level,
            "adr": 0
        }
        self.tab.append(new_entry)

        new_id_idx = len(self.tab) - 1
        current_block["last"] = new_id_idx
        return new_id_idx

    def add_builtin_procedure(self, name: str):
        """Tambah prosedur built-in (predefined) ke symbol table at global scope"""
        global_block = self.btab[0]
        link_idx = 0

        new_entry = {
            "name": name,
            "link": link_idx,
            "obj": ObjKind.PROCEDURE,
            "type": TypeKind.NOTYPE,
            "ref": 0,
            "nrm": 1,
            "lev": 0,
            "adr": 0
        }
        self.tab.append(new_entry)
        new_id_idx = len(self.tab) - 1

        return new_id_idx

    def add_type(self, name: str, type_kind: int):
        current_btab_idx = self.display[self.current_level]
        current_block = self.btab[current_btab_idx]
        link_idx = current_block["last"]

        new_entry = {
            "name": name,
            "link": link_idx,
            "obj": ObjKind.TYPE,
            "type": type_kind,
            "ref": 0,
            "nrm": 1,
            "lev": self.current_level,
            "adr": 0
        }
        self.tab.append(new_entry)
        new_id_idx = len(self.tab) - 1
        current_block["last"] = new_id_idx
        return new_id_idx

    # Lookup
    def lookup(self, name: str) -> Optional[Dict]:
        for level in range(self.current_level, -1, -1):
            btab_idx = self.display[level]
            current_id_idx = self.btab[btab_idx]["last"]

            while current_id_idx > 0:
                entry = self.tab[current_id_idx]
                if entry["name"] == name:
                    return entry
                current_id_idx = entry["link"]

        reserved_count = ReservedWords.count()
        for i in range(reserved_count):
            if self.tab[i]["name"] == name:
                 return self.tab[i]

        return None

    def lookup_current_scope(self, name: str) -> Optional[Dict]:
        btab_idx = self.display[self.current_level]
        current_id_idx = self.btab[btab_idx]["last"]

        while current_id_idx > 0:
            entry = self.tab[current_id_idx]
            if entry["name"] == name:
                return entry
            current_id_idx = entry["link"]

        return None

    def get_parameters(self, symbol: Dict) -> List[Dict]:
        if symbol['obj'] not in [ObjKind.PROCEDURE, ObjKind.FUNCTION]:
            return []

        block_ref = symbol.get('ref', 0)
        if block_ref <= 0 or block_ref >= len(self.btab):
            return []

        block = self.btab[block_ref]
        params = []
        param_count = block.get('psze', 0)
        if param_count == 0:
            return []

        current_idx = block.get('lpar', 0)
        for _ in range(param_count):
            if current_idx > 0 and current_idx < len(self.tab):
                params.append(self.tab[current_idx])
                current_idx = self.tab[current_idx]['link']

        params.reverse()
        return params

    def print_tables(self):
        print("\nTAB (Identifier Table)\n")
        print(f"{'Idx':<4} {'Name':<12} {'Link':<5} {'Obj':<10} {'Type':<5} {'Ref':<5} {'Nrm':<4} {'Lev':<4} {'Adr':<5}")
        print("-"*50)
        start_idx = ReservedWords.count()
        print(f"{'...':<4} (reserved words 0-{start_idx-1})")
        for i, entry in enumerate(self.tab):
            if i < start_idx: continue
            s_link = str(entry.get('link', 0))
            s_obj  = str(entry.get('obj', '-'))
            typ_entry = entry.get('type', 0)
            if isinstance(typ_entry, dict) and 'kind' in typ_entry:
                s_type = str(typ_entry['kind'])
            else:
                s_type = str(typ_entry)
            s_ref  = str(entry.get('ref', 0))
            s_nrm  = str(entry.get('nrm', 0))
            s_lev  = str(entry.get('lev', 0))
            s_adr  = str(entry.get('adr', '-'))
            print(f"{i:<4} {entry['name']:<12} {s_link:<5} {s_obj:<10} {s_type:<5} {s_ref:<5} {s_nrm:<4} {s_lev:<4} {s_adr:<5}")
        print("\nBTAB (Block Table)\n")
        print(f"{'Idx':<4} {'Last':<5} {'Lpar':<5} {'Psze':<5} {'Vsze':<5}")
        print("-"*50)
        for entry in self.btab:
            s_idx = str(entry.get('index', 0))
            s_last = str(entry.get('last', 0))
            s_lpar = str(entry.get('lpar', 0))
            s_psze = str(entry.get('psze', 0))
            s_vsze = str(entry.get('vsze', 0))
            print(f"{s_idx:<4} {s_last:<5} {s_lpar:<5} {s_psze:<5} {s_vsze:<5}")
        print("\nATAB (Array Table)")
        if not (self.atab):
            print("(kosong karena tidak ada array)")
            return
        print(f"{'Idx':<4} {'Xtyp':<5} {'Etyp':<5} {'Eref':<5} {'Low':<5} {'High':<5} {'Elsz':<5} {'Size':<5}")
        print("-" * 50)
        for entry in self.atab:
            s_idx  = str(entry.get('index', 0))
            s_xtyp = str(entry.get('xtyp', 0))
            s_etyp = str(entry.get('etyp', 0))
            s_eref = str(entry.get('eref', 0))
            s_low  = str(entry.get('low', 0))
            s_high = str(entry.get('high', 0))
            s_elsz = str(entry.get('elsz', 0))
            s_size = str(entry.get('size', 0))
            print(f"{s_idx:<4} {s_xtyp:<5} {s_etyp:<5} {s_eref:<5} {s_low:<5} {s_high:<5} {s_elsz:<5} {s_size:<5}")

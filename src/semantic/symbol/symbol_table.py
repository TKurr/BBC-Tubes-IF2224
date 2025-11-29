from typing import List, Optional, Any, Dict
from .constants import ReservedWords, ObjKind, TypeKind

class SymbolTable:
    def __init__(self):
        self.tab: List[Dict[str, Any]] = [] # Tabel Identifier
        self.btab: List[Dict[str, Any]] = [] # Tabel Blok
        self.atab: List[Dict[str, Any]] = [] # Tabel Array
        self.display: List[int] = [] # Stack Pointer ke BTAB
        self.current_level = 0 # Level leksikal saat ini
        
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
            "last": 0, # Pointer ke identifier terakhir (awal 0)
            "lpar": 0, # Parameter terakhir
            "psze": 0, # Ukuran parameter
            "vsze": 0 # Ukuran variabel
        })
        self.display = [0]

    # ==========================================================
    # Deklarasi Lingkup Dalam 
    # ==========================================================
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

    # ==========================================================
    # ADD ENTRIES
    # ==========================================================
    def add_variable(self, name: str, type_kind: int, size: int = 1):
        """Tambah variabel lokal"""
        current_btab_idx = self.display[self.current_level]
        current_block = self.btab[current_btab_idx]
        
        # Logika Linked List & Alamat
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
        
        # Perbarui Blok
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
        
        # Perbarui Blok (lpar & psze) [Ref: PDF Hal 13]
        new_id_idx = len(self.tab) - 1
        current_block["last"] = new_id_idx
        current_block["lpar"] = new_id_idx 
        current_block["psze"] += 1
        return new_id_idx
    
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
            "type": TypeKind.NOTYPE, # Nanti diupdate kalau Function (return type)
            "ref": 0,
            "nrm": 1,
            "lev": self.current_level,
            "adr": 0
        }
        self.tab.append(new_entry)
        
        new_id_idx = len(self.tab) - 1
        current_block["last"] = new_id_idx
        return new_id_idx

    # ==========================================================
    # LOOKUP
    # ==========================================================
    def lookup(self, name: str) -> Optional[Dict]:
        # Cari di Scope Pengguna (menelusuri Display & link)
        for level in range(self.current_level, -1, -1):
            btab_idx = self.display[level]
            current_id_idx = self.btab[btab_idx]["last"]
            
            while current_id_idx > 0: 
                entry = self.tab[current_id_idx]
                if entry["name"] == name:
                    return entry
                current_id_idx = entry["link"]
        
        # Cari di Kata Cadangan (Reserved Words)
        reserved_count = ReservedWords.count()
        for i in range(reserved_count):
            if self.tab[i]["name"] == name:
                 return self.tab[i]
                 
        return None
    
    def lookup_current_scope(self, name: str) -> Optional[Dict]:
        """Cari identifier hanya di scope saat ini"""
        btab_idx = self.display[self.current_level]
        current_id_idx = self.btab[btab_idx]["last"]
        
        while current_id_idx > 0:
            entry = self.tab[current_id_idx]
            if entry["name"] == name:
                return entry
            current_id_idx = entry["link"]
        
        return None
    
    def add_type(self, name: str, type_kind: int):
        """Tambah deklarasi tipe"""
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
    
    def get_parameters(self, symbol: Dict) -> List[Dict]:
        """Ambil parameter untuk suatu prosedur atau fungsi"""
        if symbol['obj'] not in [ObjKind.PROCEDURE, ObjKind.FUNCTION]:
            return []
        
        # Ambil referensi blok untuk prosedur/fungsi ini
        block_ref = symbol.get('ref', 0)
        if block_ref <= 0 or block_ref >= len(self.btab):
            return []
        
        block = self.btab[block_ref]
        params = []
        
        # Ambil jumlah parameter dan index parameter terakhir
        param_count = block.get('psze', 0)
        if param_count == 0:
            return []
        
        # Telusuri linked list dari lpar mundur untuk mendapatkan semua parameter
        current_idx = block.get('lpar', 0)
        for _ in range(param_count):
            if current_idx > 0 and current_idx < len(self.tab):
                params.append(self.tab[current_idx])
                current_idx = self.tab[current_idx]['link']
        
        # Dibalik agar urutan sesuai deklarasi
        params.reverse()
        return params
        
    def print_tables(self):
        """Cetak tabel untuk debugging"""
        print("\n=== TAB (Identifier Table) ===")
        print(f"{'Idx':<4} {'Name':<12} {'Link':<5} {'Obj':<10} {'Type':<5} {'Ref':<5} {'Nrm':<4} {'Lev':<4} {'Adr':<5}")
        
        start_idx = ReservedWords.count()
        for i, entry in enumerate(self.tab):
            if i < start_idx: continue 
            print(f"{i:<4} {entry['name']:<12} {entry['link']:<5} {entry['obj']:<10} {entry['type']:<5} {entry['ref']:<5} {entry['nrm']:<4} {entry['lev']:<4} {entry['adr']:<5}")

        print("\n=== BTAB (Block Table) ===")
        print(f"{'Idx':<4} {'Last':<5} {'Lpar':<5} {'Psze':<5} {'Vsze':<5}")
        for entry in self.btab:
            print(f"{entry['index']:<4} {entry['last']:<5} {entry['lpar']:<5} {entry['psze']:<5} {entry['vsze']:<5}")


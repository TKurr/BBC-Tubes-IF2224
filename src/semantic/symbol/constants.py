class ReservedWords:
    LIST = [
        "program", "variabel", "mulai", "selesai", "jika", "maka",
        "selain_itu", "selama", "lakukan", "untuk", "ke", "turun_ke", "larik", "dari", "true",
        "false", "prosedur", "fungsi", "konstanta", "tipe", "sampai",
        "ulangi", "rekaman", "kasus", "dan", "atau", "tidak", "bagi", "mod"
    ]

    @staticmethod
    def count():
        return len(ReservedWords.LIST)

class ObjKind:
    CONSTANT = "constant"
    VARIABLE = "variable"
    TYPE     = "type"
    PROCEDURE= "procedure"
    FUNCTION = "function"
    PROGRAM  = "program"
    RESERVED = "reserved"

class TypeKind:
    NOTYPE  = 0
    INTEGER = 1
    REAL    = 2
    BOOLEAN = 3
    CHAR    = 4
    ARRAY   = 5
    RECORD  = 6


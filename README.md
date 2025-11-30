<div align="center">
   <img width=100% src="https://capsule-render.vercel.app/api?type=waving&height=300&color=0:282C34,25:181921,75:313642,100:282C34&text=BigBlackCompiler&fontColor=F7DC6F" />
</div>

# BBC-Tubes-IF2224

> **Implementasi Pascal-S Lexical & Syntax Analyzer "**

> Dipakai untuk kebutuhan `Tugas Besar IF2224 TBFO`

## Identitas Kelompok

**Kelompok**: BBC
**Mata Kuliah**: IF2224 Teori Bahasa Formal dan Otomata  
**Milestone**: 3 - Semantic Analyzer

**Anggota Kelompok**:

1. Brian Ricardo Tamin - 13523126
2. Jovandra Otniel P. S. - 13523141
3. Andrew Tedjapratama - 13523148
4. Theo Kurniady - 13523154

---

## Deskripsi Program
### Milestone-1
Pascal-S Lexical Analyzer adalah program yang melakukan **analisis leksikal** (lexical analysis) pada bahasa Pascal-S menggunakan **Deterministic Finite Automata (DFA)**. Program ini mengubah source code Pascal-S dari rangkaian karakter mentah menjadi **token** yang terstruktur.

### Milestone-2
Pascal-S Syntax Analyzer adalah program yang melakukan analisis sintaks (syntax analysis) pada source code Pascal-S untuk memastikan bahwa susunan token mengikuti aturan grammar Pascal-S. Program ini menerima token hasil lexical analyzer dan membangunnya menjadi sebuah parse tree menggunakan metode Recursive Descent Parsing.

### Milestone-3
Pascal-S Semantic Analyzer adalah program yang melakukan **analisis semantik** (semantic analysis) pada source code Pascal-S untuk mengecek kebenaran makna pada pohon sintaks (AST). Program ini memvalidasi aturan semantik seperti:
- Deklarasi dan penggunaan identifier (variabel, konstanta, fungsi, prosedur)
- Kompatibilitas tipe data dalam operasi dan assignment
- Scope dan visibility identifier
- Jumlah dan tipe parameter pada pemanggilan fungsi/prosedur

### Fitur:
#### Milestone-1
-   Mengenali 20 jenis token sesuai spesifikasi Pascal-S
-   Menggunakan DFA yang dikonfigurasi melalui file JSON
-   Error handling dengan informasi lokasi (line dan column)

#### Milestone-2
- Menganalisis struktur program Pascal-S berdasarkan grammar pada spesifikasi
- Membangun parse tree lengkap yang merepresentasikan struktur sintaks
- Memvalidasi setiap konstruksi sintaksis, memastikan token membentuk struktur yang benar (misalnya: urutan deklarasi, bentuk ekspresi, tipe statement, dan aturan prioritas operator)
- Error handling detail dengan informasi lokasi (line dan column) menggunakan ParseError

#### Milestone-3
- Implementasi TAB (Identifier Table), BTAB (Block Table), dan ATAB (Array Table) untuk manajemen identifier
- Validasi tipe data untuk operasi aritmetika, relasional, logika, dan assignment
- Pengelolaan nested scope untuk prosedur/fungsi dengan display vector
- Deteksi error seperti:
  - Undeclared/redeclared identifier
  - Type mismatch dalam operasi dan assignment
  - Invalid array index (non-integer)
  - Argument count/type mismatch pada pemanggilan fungsi/prosedur
  - Assignment ke konstanta
- Tipe Data yang Dikenali:
  - Tipe primitif: `integer`, `real`, `boolean`, `char`, `string`
  - Tipe kompleks: `array`, `record`
  - Kompatibilitas tipe (integer dan real, char dan string)
- Menambahkan atribut semantik (tipe, level, index tabel) pada node AST

---

## Requirements

-   **Python 3.8+**
-   Tidak memerlukan library eksternal (hanya standard library)

---

## Cara Instalasi

```bash
git clone https://github.com/[username]/BBC-Tubes-IF2224.git
cd BBC-Tubes-IF2224
```

## Cara Penggunaan Program

### Format Command:

```bash
python main.py {path/to/input.pas}
```

### Contoh:

```bash
python main.py milestone-1/input/input-1.pas
```
atau
```bash
python main.py milestone-2/input/input-1.pas
```
atau
```bash
python main.py milestone-3/input/input-1.pas
```

### Contoh Input (`program.pas`):

```pascal
program Hello;
var
  a, b: integer;
begin
  a := 5;
  b := a + 10;
end.
```

### Output:
#### Milestone-1
```
KEYWORD(program)
IDENTIFIER(Hello)
SEMICOLON(;)
KEYWORD(var)
IDENTIFIER(a)
COMMA(,)
IDENTIFIER(b)
COLON(:)
KEYWORD(integer)
SEMICOLON(;)
KEYWORD(begin)
IDENTIFIER(a)
ASSIGN_OPERATOR(:=)
NUMBER(5)
SEMICOLON(;)
IDENTIFIER(b)
ASSIGN_OPERATOR(:=)
IDENTIFIER(a)
ARITHMETIC_OPERATOR(+)
NUMBER(10)
SEMICOLON(;)
KEYWORD(end)
DOT(.)
```

#### Milestone-2
```
<program>
├── <program-header>
│   ├── KEYWORD(program)
│   ├── IDENTIFIER(Hello)
│   └── SEMICOLON(;)
├── <declaration-part>
│   └── <var-declaration>
│       ├── KEYWORD(variabel)
│       ├── <identifier-list>
│       │   ├── IDENTIFIER(a)
│       │   ├── COMMA(,)
│       │   └── IDENTIFIER(b)
│       ├── COLON(:)
│       ├── <type>
│       │   └── KEYWORD(integer)
│       └── SEMICOLON(;)
├── <compound-statement>
│   ├── KEYWORD(mulai)
│   ├── <statement-list>
│   │   ├── <assignment-statement>
│   │   │   ├── <variable>
│   │   │   │   └── IDENTIFIER(a)
│   │   │   ├── ASSIGN_OPERATOR(:=)
│   │   │   └── <expression>
│   │   │       └── <simple-expression>
│   │   │           └── <term>
│   │   │               └── <factor>
│   │   │                   └── NUMBER(5)
│   │   ├── SEMICOLON(;)
│   │   ├── <assignment-statement>
│   │   │   ├── <variable>
│   │   │   │   └── IDENTIFIER(b)
│   │   │   ├── ASSIGN_OPERATOR(:=)
│   │   │   └── <expression>
│   │   │       └── <simple-expression>
│   │   │           ├── <term>
│   │   │           │   └── <factor>
│   │   │           │       └── <variable>
│   │   │           │           └── IDENTIFIER(a)
│   │   │           ├── ARITHMETIC_OPERATOR(+)
│   │   │           └── <term>
│   │   │               └── <factor>
│   │   │                   └── NUMBER(10)
│   │   ├── SEMICOLON(;)
│   │   ├── <procedure/function-call>
│   │   │   ├── IDENTIFIER(writeln)
│   │   │   ├── LPARENTHESIS(()
│   │   │   ├── <parameter-list>
│   │   │   │   ├── <expression>
│   │   │   │   │   └── <simple-expression>
│   │   │   │   │       └── <term>
│   │   │   │   │           └── <factor>
│   │   │   │   │               └── STRING_LITERAL('Result = ')
│   │   │   │   ├── COMMA(,)
│   │   │   │   └── <expression>
│   │   │   │       └── <simple-expression>
│   │   │   │           └── <term>
│   │   │   │               └── <factor>
│   │   │   │                   └── <variable>
│   │   │   │                       └── IDENTIFIER(b)
│   │   │   └── RPARENTHESIS())
│   │   └── SEMICOLON(;)
│   └── KEYWORD(selesai)
└── DOT(.)
```

#### Milestone-3
```
============================= SEMANTIC ANALYSIS + SYMBOL TABLE =============================


TAB (Identifier Table)

Idx  Name         Link  Obj        Type  Ref   Nrm  Lev  Adr  
--------------------------------------------------
...  (reserved words 0-28)
29   Hello        0     program    0     0     1    0    0    
30   a            0     variable   1     0     1    0    0    
31   b            30    variable   1     0     1    0    1    
32   writeln      0     procedure  0     0     1    0    0    

BTAB (Block Table)

Idx  Last  Lpar  Psze  Vsze 
--------------------------------------------------
0    31    0     0     2    
1    0     0     0     0    

ATAB (Array Table)
(kosong karena tidak ada array)

================================= DECORATED AST =================================

└─ ProgramNode(name: 'Hello') → tab_index:29, type:void, lev:0
   ├─ Declarations
   │  ├─ VarDecl('a') → tab_index:30, type:integer, lev:0
   │  └─ VarDecl('b') → tab_index:31, type:integer, lev:0
   └─ Block → block_index:1, lev:1
      ├─ Assign('a' := 5) → type:void
      │  ├─ target 'a' → tab_index:30, type:integer, lev:0
      │  └─ value 5 → type:integer
      ├─ Assign('b' := expr) → type:void
      │  ├─ target 'b' → tab_index:31, type:integer, lev:0
      │  └─ BinOp '+' → type:integer
      │     ├─ target 'a' → tab_index:30, type:integer, lev:0
      │     └─ value 10 → type:integer
      └─ ProcedureFunctionCall('writeln') → predefined, tab_index:32
         ├─ String ('Result = ') → type:string
         └─ target 'b' → tab_index:31, type:integer, lev:0

```

## Pembagian Tugas
### Milestone-1
| Nama                  | NIM      | Tugas                                       | Kontribusi |
| --------------------- | -------- | ------------------------------------------- | ---------- |
| Brian Ricardo Tamin   | 13523126 | Diagram DFA, laporan, perancangan DFA rules | 25%        |
| Jovandra Otniel P. S. | 13523141 | Testing dan debugging errors serta laporan  | 25%        |
| Andrew Tedjapratama   | 13523148 | Implementasi token, laporan                 | 25%        |
| Theo Kurniady         | 13523154 | DFA Engine, rules, dan lexer, laporan       | 25%        |

### Milestone-2
| Nama                  | NIM      | Tugas                                                                                                     | Kontribusi |
| --------------------- | -------- | --------------------------------------------------------------------------------------------------------- | ---------- |
| Brian Ricardo Tamin   | 13523126 | Refine modularity and lexical error, parse expression, term, factor, operators                            | 25%        |
| Jovandra Otniel P. S. | 13523141 | Parse identifier , array, range, statement, statement_list                                                | 25%        |
| Andrew Tedjapratama   | 13523148 | Parse Node, init Recursive Descent, Parse Variable, Parse type & type-definition, parse statement detail  | 25%        |
| Theo Kurniady         | 13523154 | Parse declarations, parameter,  variable-index, rekaman, & kasus                                          | 25%        |

### Milestone-3
| Nama                  | NIM      | Tugas                                                                                                     | Kontribusi |
| --------------------- | -------- | --------------------------------------------------------------------------------------------------------- | ---------- |
| Brian Ricardo Tamin   | 13523126 | Implementasi Symbol Table (TAB, BTAB, ATAB), scope management, AST decoration                             | 25%        |
| Jovandra Otniel P. S. | 13523141 | Type checker, semantic analyzer untuk statements dan expressions                                          | 25%        |
| Andrew Tedjapratama   | 13523148 | Semantic error classes, AST builder integration, testing dan debugging                                    | 25%        |
| Theo Kurniady         | 13523154 | Semantic analyzer untuk declarations, function/procedure calls, laporan                                   | 25%        |

<div align="center">
   <img width=100% src="https://capsule-render.vercel.app/api?type=waving&height=120&color=0:282C34,25:181921,75:313642,100:1e3a8a&section=footer" />
</div>

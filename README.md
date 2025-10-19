<div align="center">
   <img width=100% src="https://capsule-render.vercel.app/api?type=waving&height=300&color=0:282C34,25:181921,75:313642,100:282C34&text=BigBlackCompiler&fontColor=F7DC6F" />
</div>

# BBC-Tubes-IF2224

> **Implementasi Pascal-S Lexical Analyzer"**

> Dipakai untuk kebutuhan `Tugas Besar IF2224 TBFO`

## Identitas Kelompok

**Kelompok**: BBC
**Mata Kuliah**: IF2224 Teori Bahasa Formal dan Otomata  
**Milestone**: 1 - Lexical Analysis

**Anggota Kelompok**:

1. Brian Ricardo Tamin - 13523126
2. Jovandra Otniel P. S. - 13523141
3. Andrew Tedjapratama - 13523148
4. Theo Kurniady - 13523154

---

## Deskripsi Program

Pascal-S Lexical Analyzer adalah program yang melakukan **analisis leksikal** (lexical analysis) pada bahasa Pascal-S menggunakan **Deterministic Finite Automata (DFA)**. Program ini mengubah source code Pascal-S dari rangkaian karakter mentah menjadi **token** yang terstruktur.

### Fitur:

-   Mengenali 20 jenis token sesuai spesifikasi Pascal-S
-   Menggunakan DFA yang dikonfigurasi melalui file JSON
-   Error handling dengan informasi lokasi (line dan column)

---

## Requirements

-   **Python 3.8+**
-   Tidak memerlukan library eksternal (hanya standard library)

---

## Cara Instalasi

```bash
git clone https://github.com/[username]/K01-Tubes-IF2224.git
cd K01-Tubes-IF2224
```

## Cara Penggunaan Program

### Format Command:

```bash
python src/main.py
```

### Contoh:

```bash
python src/main.py test/milestone-1/input-1.pas
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

## Pembagian Tugas

| Nama                  | NIM      | Tugas                                       | Kontribusi |
| --------------------- | -------- | ------------------------------------------- | ---------- |
| Brian Ricardo Tamin   | 13523126 | Diagram DFA, laporan, perancangan DFA rules | 25%        |
| Jovandra Otniel P. S. | 13523141 | Testing dan debugging errors serta laporan  | 25%        |
| Andrew Tedjapratama   | 13523148 | Implementasi token, laporan                 | 25%        |
| Theo Kurniady         | 13523154 | DFA Engine, rules, dan lexer, laporan       | 25%        |

Perancangan DFA, implementasi DFA Engine

<div align="center">
   <img width=100% src="https://capsule-render.vercel.app/api?type=waving&height=120&color=0:282C34,25:181921,75:313642,100:1e3a8a&section=footer" />
</div>

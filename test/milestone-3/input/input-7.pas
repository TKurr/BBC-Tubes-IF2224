program testall;
tipe
  Rec = rekaman
    z: integer;
    t: larik[1 .. 2] dari integer
  selesai;
variabel
  a: integer;
  b: larik[1 .. 3] dari Rec;
fungsi f(n: integer): integer;
mulai
  f := n + 1;
selesai;
prosedur g(q: integer);
mulai
  b[1].t[2] := q * 2;
selesai;
mulai
  a := f(2) * b[2].z;
  b[1].z := 5;
  jika a < 10 maka
    g(a)
  selain_itu
    a := b[1].t[2];
  kasus a dari
    1: a := 2;
    2: g(3);
    3: a := f(7)
  ;
selesai.
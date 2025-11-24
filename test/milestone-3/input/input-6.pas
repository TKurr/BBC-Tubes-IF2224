program mega;
tipe
  Index = 1 .. 10;
  Pair = rekaman
    a, b: integer
  selesai;
variabel
  x, y: integer;
  arr: larik[1 .. 5] dari integer;
  rec: rekaman
    p: Pair;
    v: larik[1 .. 3] dari integer
  selesai;
prosedur foo(a: integer; b: integer);
mulai
  a := b + 1;
selesai;
fungsi bar(t: integer): integer;
mulai
  bar := t * 2;
selesai;
mulai
  rec.p.a := arr[3] + bar(2);
  rec.v[2] := rec.p.a * 3;
  jika rec.v[2] > 10 maka
    x := 1
  selain_itu
    x := 2;
  selama x < 5 lakukan
    x := x + 1;
  untuk y := 1 ke 3 lakukan
    arr[y] := arr[y] + 1;
  ulangi
    x := x - 1
  sampai x = 0;
selesai.
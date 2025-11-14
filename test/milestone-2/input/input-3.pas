program RangesLoops;
variabel
  i: integer;
  a: larik[0 .. 3] dari integer;
mulai
  a[0] := 1;
  untuk i := 0 ke 3 lakukan
    a[i] := i;
  untuk i := 3 turun-ke 0 lakukan
    a[i] := a[i] + 1;
  jika a[1] < a[2] maka
    a[1] := a[2];
  selama i > 0 lakukan
    i := i - 1;
  writeln('ok', a[1]);
selesai.

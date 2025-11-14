program Hello2;
variabel
  a, b, i: integer;
  arr: larik[1 .. 5] dari integer;

mulai
  a := 5;
  b := a + 10;
  writeln('Result = ', b);
  untuk i := 1 ke 5 lakukan
  mulai
    arr[i] := i + 1;
    writeln(arr[i]);
  selesai;
selesai.

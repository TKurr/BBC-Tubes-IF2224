program DeclsProcFunc;
konstanta
  K = 10;
variabel
  i: integer;
  r: real;
  ch: char;
  ok: boolean;
  arr: larik[1 .. 10] dari integer;

prosedur IncVar(z: integer);
mulai
  z := z + 1;
selesai;

fungsi AddOne(t: integer): integer;
mulai
  AddOne := t + 1;
selesai;

mulai
  r := 3.14;
  ch := 'A';
  ok := true dan tidak false;
  arr[1] := 2;
  jika (arr[1] >= K) maka
    arr[1] := AddOne(arr[1])
  selain_itu
    IncVar(arr[1]);
  writeln('Value: ', arr[1], '.');
selesai.

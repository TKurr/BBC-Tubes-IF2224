program Ops;
variabel
  x, y: integer;
  r: real;
  ch: char;
  ok: boolean;
mulai
  x := 10;
  y := 3;
  r := 12.5;
  ch := 'Z';
  ok := (x > y) dan tidak (x = y);
  x := x + y - 2 * (y bagi 2) / 1;
  x := x mod y;
  jika x <= y maka
    x := y
  selain_itu
    x := y + 1;
  writeln('done ', x);
selesai.
program TestArrayRecord;

tipe
  Point = rekaman
    x, y: integer
  selesai;

variabel
  p: Point;
  matrix: larik[1 .. 5] dari integer;
  i, total: integer;

mulai
  p.x := 10;
  p.y := 20;
  total := p.x * p.y;

  untuk i := 1 ke 5 lakukan
    matrix[i] := i * 2;

  matrix[1] := matrix[1] + p.x;

  writeln(total);
selesai.

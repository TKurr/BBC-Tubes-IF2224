program Ops;
var
  x, y: integer;
  r: real;
  ch: char;
  ok: boolean;
begin
  x := 10;
  y := 3;
  r := 12.5;
  ch := 'Z';
  ok := (x > y) and not (x = y)
  x := x + y - 2 * (y div 2) / 1;
  x := x mod y;
  if x <= y then
    x := y
  else
    x := y + 1;
  writeln('done ', x);
end.
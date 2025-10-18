program RangesLoops;
var
  i: integer;
  a: array[0..3] of integer;
begin
  a[0] := 1;
  for i := 0 to 3 do
    a[i] := i;
  for i := 3 downto 0 do
    a[i] := a[i] + 1;
  if a[1] < a[2] then
    a[1] := a[2];
  while i > 0 do
    i := i - 1;
  writeln('ok', a[1]);
end.
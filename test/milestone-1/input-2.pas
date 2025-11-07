program Hello2;
var
  a, b, i: integer;
  arr: array[1 .. 5] of integer;

begin
  a := 5;
  b := a + 10;
  writeln('Result = ', b);
  for i := 1 to 5 do
  begin
    arr[i] := i + 1;
    writeln(arr[i]);
  end;
end.

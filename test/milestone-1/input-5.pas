program DeclsProcFunc;
const
  K = 10;
type
  Index = 1..5;
var
  i: integer;
  r: real;
  ch: char;
  ok: boolean;
  arr: array[Index] of integer;

procedure IncVar(var z: integer);
begin
  z := z + 1;
end;

function AddOne(t: integer): integer;
begin
  AddOne := t + 1;
end;

begin
  r := 3.14;
  ch := 'A';
  ok := true and not false;   
  arr[1] := 2;
  if (arr[1] >= K) then
    arr[1] := AddOne(arr[1])
  else
    IncVar(arr[1]);
  writeln('Value: ', arr[1], '.');
end.
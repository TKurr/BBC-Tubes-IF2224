program TestProc;

variabel
  global_x, global_y: integer;

prosedur swap(variabel a: integer; variabel b: integer);
variabel temp: integer;
mulai
  temp := a;
  a := b;
  b := temp;
selesai;

fungsi add(a: integer; b: integer): integer;
mulai
  add := a + b;
selesai;

mulai
  global_x := 100;
  global_y := 200;

  swap(global_x, global_y);

  global_x := add(global_x, global_y);
selesai.

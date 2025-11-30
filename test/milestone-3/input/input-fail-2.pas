program TestFailScope;

variabel
  global_var: integer;

prosedur localScope;
variabel
  local_var: integer;
mulai
  local_var := 10;
selesai;

mulai
  global_var := 20;

  local_var := 5;

  global_var.x := 10;
selesai.

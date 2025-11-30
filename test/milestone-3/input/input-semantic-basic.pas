program TestBasic;

variabel
  i, limit, sum: integer;
  flag: boolean;

mulai
  limit := 10;
  sum := 0;
  flag := true;

  untuk i := 1 ke limit lakukan
    sum := sum + i;

  jika sum > 50 maka
    flag := false
  selain_itu
    flag := true;

  selama limit > 0 lakukan
  mulai
    limit := limit - 1;
    writeln(limit);
  selesai;
selesai.

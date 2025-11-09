program TestSemuaLoop;

variabel
  i: integer;
  j: integer;
  k: integer;

mulai
  i := 0;
  selama i < 5 lakukan
    i := i + 1;
    
  untuk j := 1 ke 3 lakukan
    i := i + j;
    
  untuk j := 3 turun_ke 1 lakukan
    i := i - j;

  k := 10;
  ulangi
    k := k - 1;
  sampai k = 0;
  
selesai.
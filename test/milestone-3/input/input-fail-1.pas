program TestFailType;

variabel
  angka: integer;
  status: boolean;

mulai
  angka := 10;
  status := true;

  angka := status;

  jika angka + status > 10 maka
    status := false;
selesai.

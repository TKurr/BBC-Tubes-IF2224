program TestSubprogramJika;

variabel
  status_program: boolean;

fungsi ApakahSelesai(nilai: integer): boolean;
mulai
  jika nilai = 100 maka
    ApakahSelesai := true
  selain_itu
    ApakahSelesai := false;
selesai;

prosedur AturStatus(status: boolean);
mulai
  status_program := status;
selesai;

mulai
  AturStatus(false);
  jika ApakahSelesai(100) maka
    AturStatus(true);
selesai.
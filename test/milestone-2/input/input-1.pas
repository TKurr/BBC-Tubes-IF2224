program TestDeklarasiLengkap;

konstanta
  MAX_SIZE = 100;
  NAMA_KURSUS = 'IF2224';

tipe
  Angka = integer;
  Pecahan = real;
  Status = boolean;
  Huruf = char;
  DaftarAngka = larik [1 .. MAX_SIZE] dari Angka;

variabel
  skor: DaftarAngka;
  nilai: Pecahan;
  lulus: Status;

mulai
  nilai := 90.5;
selesai.
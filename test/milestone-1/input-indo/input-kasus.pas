program TestKasusDiagram;

variabel
  pilihan: integer;
  hasil_A: integer;
  hasil_B: integer;

mulai
  pilihan := 3;
  
  kasus pilihan dari
    1: hasil_A := 100;
    
    2: hasil_A := 200;
    
    3: mulai
         hasil_A := 300;
         hasil_B := 333;
       selesai;
    
    4: hasil_A := 400
  
selesai.
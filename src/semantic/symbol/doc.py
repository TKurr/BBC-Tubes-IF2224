# CONTOH : 



program Utama;             { Global Scope (Level 0) }

   prosedur Hitung(a: integer);
   var hasil: integer;     { Local Scope (Level 1) }
   begin
       ...
   end;

begin
   ...
end.





st.add_procedure("Utama", ObjKind.PROGRAM)
# daftarin nama prosedur 'Hitung' di Scope Bapaknya (Global/Level 0)
proc_idx = st.add_procedure("Hitung", ObjKind.PROCEDURE)

# Masuk ke Body Prosedur,  buka scope baru (Level 1)
st.enter_scope()

# add Parameter 'a'
# 'a' punya Level 1. is_var=False karena pass-by-value.
st.add_parameter("a", TypeKind.INTEGER, is_var=False)

# add variabel lokal hasil
# 'hasil' punya level 1
st.add_variable("hasil", TypeKind.INTEGER)

# Keluar Scope -> balik ke Global (Level 0)
st.exit_scope()

# Lanjut parse lagi di level 0
...
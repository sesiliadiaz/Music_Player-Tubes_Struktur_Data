## Anggota Kelompok :
1. Zerlina Agustiya P (103102400009)
2. Sarah Aulia B (103102400051)
3. Sesilia W N Diaz (103102400074)

# Music Player (Python GUI)

Music Player merupakan aplikasi pemutar musik berbasis **Graphical User Interface (GUI)** yang dikembangkan menggunakan bahasa pemrograman **Python** dengan memanfaatkan pustaka **Tkinter**.  
Aplikasi ini dirancang untuk memudahkan pengguna dalam memutar musik serta mengelola data lagu dan playlist secara terstruktur.

---

## Fitur Aplikasi

### A. Admin Mode
Admin merupakan peran yang memiliki hak akses penuh terhadap pengelolaan data lagu pada library utama.  
Fitur yang tersedia untuk admin meliputi:
1. Menambahkan lagu  
2. Melihat daftar lagu  
3. Mengubah data lagu  
4. Menghapus lagu  
5. Fitur login  

---

### B. User Mode
User merupakan peran yang berfokus pada pemutaran lagu dan pengelolaan playlist.  
Fitur user dirancang untuk memberikan pengalaman pemutaran musik yang fleksibel dan mudah digunakan.  
Fitur yang tersedia untuk user meliputi:
1. Pencarian lagu  
2. Play dan pause lagu  
3. Navigasi lagu (next dan previous)  
4. Pengurutan lagu  
5. Fitur antrean lagu  
6. Menjadikan lagu sebagai favorit  
7. Manajemen playlist
8. Fitur history lagu 

---

## Struktur Data yang Digunakan

### 1. List
Struktur data **list** digunakan untuk menyimpan library utama lagu.  
Setiap elemen dalam list merepresentasikan satu data lagu dalam bentuk record.  
Penggunaan list memungkinkan aplikasi untuk melakukan iterasi, pencarian, serta pengelolaan data lagu secara efisien.  
Struktur data ini dipilih karena sesuai untuk menyimpan kumpulan data lagu yang bersifat umum dan sering diakses.

---

### 2. Doubly Linked List
**Doubly linked list** digunakan untuk merepresentasikan playlist lagu.  
Setiap playlist terdiri dari node-node lagu yang saling terhubung secara dua arah.  
Struktur data ini memungkinkan navigasi lagu ke arah berikutnya maupun sebelumnya dengan mudah, serta mempermudah proses penambahan dan penghapusan lagu tanpa harus menggeser elemen lain.

---

### 3. Dictionary (Record)
Setiap lagu direpresentasikan menggunakan **record dalam bentuk dictionary**.  
Record ini menyimpan atribut lagu seperti:
- ID  
- Judul  
- Artis  
- Genre  
- Album  
- Tahun rilis  
- Durasi lagu  

Penggunaan dictionary memudahkan pengelolaan dan pembaruan data lagu serta mendukung proses penyimpanan data ke dalam berkas **JSON**.

---

## Cara Menjalankan Aplikasi Music Player
### 1. Persiapan Awal
- Python 3.8 atau lebih baru
- Sistem operasi Windows / macOS / Linux
- File aplikasi.py

### 2. Simpan File
- Simpan kode sebagai aplikasi.py
- Letakkan di satu folder

### 3. Jalankan Aplikasi
**Lewat Terminal / CMD**
- Masuk ke folder tempat file berada
```bash
cd path/ke/MusicPlayer
```
- Lalu jalankan:
```bash
python aplikasi.py
```

### 4. Pilih Mode Penggunaan
#### User Mode
User bisa:
- Mencari lagu
- Memutar lagu
- Membuat playlist
- Menambahkan lagu ke favorite
- Mengelola antrean lagu
- Melihat history lagu 
#### Admin Mode
Login dengan:
```
Username : anakmalem
Password : tel-u24
```
Admin bisa:
- Menambah lagu
- Mengedit data lagu (kecuali ID)
- Menghapus lagu
- Semua fitur user
 
### 5. Cara Menambahkan Lagu (Admin)
- Login sebagai Admin
- Klik tombol Tambah Lagu

Isi:
- ID lagu
- Judul
- Artis
- Genre
- Album
- Tahun
- Durasi
- Cover album
- Klik Simpan
Data lagu otomatis tersimpan ke music_data.json 

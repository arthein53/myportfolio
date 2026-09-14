Nama : Arlen

NPM : 2506613514

Kelas : PBP B


### TUGAS 1
## JAWABAN PERTANYAAN REFLEKTIF
1. Ya, saya menggunakan elemen semantik HTML5 seperti <section>, <article>, <header>, <nav>, dan <footer>. Elemen <section> saya gunakan untuk memisahkan bagian utama portofolio seperti About Me, Projects, Skills, dan Contact. Untuk setiap project, saya menggunakan <article> karena setiap project merupakan konten yang berdiri sendiri dan punya judul, deskripsi, tech stack yang digunakan, serta link bukti project. Elemen-elemen tersebut sangat membantu terutama dalam membuat kode saya readable dan clean.

2. Bagi saya, tantangan utama saat membuat tampilan responsif adalah mengatur perubahan layout dari desktop ke mobile. Di desktop, beberapa elemen dapat ditampilkan secara horizontal seperti navigasi, foto profil dan deskripsi, atau daftar project dalam beberapa kolom. Namun, di mobile elemen-elemen tersebut harus ditumpuk vertikal agar tetap mudah dibaca dan tidak menyebabkan horizontal scrolling. Saya mengevaluasi prioritas berdasarkan fungsi dan keterbacaan informasi. Konten utama seperti identitas, deskripsi, dan project harus terlihat jelas. Elemen yang bersifat pelengkap seperti dekorasi atau teks yang terlalu panjang, dapat dikecilkan, dipindahkan, atau dibuat lebih sederhana. Saya menggunakan media query untuk mengubah jumlah kolom pada grid, ukuran font, jarak antar elemen, dll agar cocok untuk layar kecil.

3. Yang saya rasakan, batasan utama static web ini adalah semua konten harus diupdate secara manual di file HTML. Kalau ingin menambahkan data project baru atau update experience dan skill, saya harus mengubah kode lalu melakukan deploy ulang. Static web juga belum dapat menyediakan banyak fitur seperti formulir kontak yang bisa kirim pesan direct ke email, fitur search proyek, dll. Pada step selanjutnya, saya ingin menambahkan formulir kontak yang terhubung ke backend atau layanan email agar guest bisa mengirim pesan langsung dari website. Saya juga ingin menyiapkan data proyek dalam format terpisah, misal mungkin JSON atau database, sehingga daftar proyek bisa ditampilkan secara dinamis dan lebih mudah di-update. 

## AI DISCLOSURE
Dalam pengerjaan Tugas 1 saya menggunakan bantuan dari GPT-5.6-terra terutama dalam elemen-elemen JavaScript untuk keperluan button dan audio player. Dalam penggunaan AI sendiri, saya menggunakan prompting dengan pendekatan "teach and explain to me ..." dibandingkan secara langsung meminta AI mengerjakan kodenya. Hal ini saya lakukan agar dapat benar-benar memahami apa yang menyusun website portfolio saya, serta secara tidak langsung juga menghemat token karena saya lalu bisa dengan mudah meng-customize sendiri sesuai yang saya inginkan (tidak ketergantungan).

AI juga membantu saya dalam pemilihan color palette, berhubung saya kurang berpengalaman dalam bidang design, jadi saya mendiskusikannya dengan AI terlebih dahulu. Selain itu, AI juga menyarankan dan mencontohkan penggunaan atribut aria dalam beberapa elemen. Atribut ini sendiri disarankan oleh AI dengan fungsi yang mendukung kejelasan text to speech. Atribut ini saya pakai di awal pengerjaan namun tidak terlalu di commit-commit terakhir karena efisiensi waktu.

Kegunaan AI yang lain adalah untuk mendapatkan informasi terkait properti CSS yang sesuai dengan cepat. Misal saya ingin membuat animasi looping ke kiri, saya akan bertanya elemen apa yang dapat mewujudkan visi ini lalu mengaplikasikannya dalam kode saya.

Detail section yang dibantu AI:
1. Light/Dark Theme Button dan implementasinya
2. Skills Loop Animation
3. Discography Audio Playback
4. Pemilihan Color Palette


### TUGAS 2
## JAWABAN PERTANYAAN REFLEKTIF
1. Saat user buka homepage, yaitu http://localhost:8000/ (local) atau https://rafael-arlen-myportfolio.pws.cs.ui.ac.id/ (production), browser mengirim HTTP request ke server Django. Request akan masuk ke portfolio/urls.py sebagai file routing utama project. path('', include('main.urls')) membuat request diteruskan ke main/urls.py karena URL yang dibuka adalah /. Di main/urls.py, path "" diarahkan ke view show_main. Lalu, Django akan run fungsi show_main() pada main/views.py. View berfungsi menyiapkan data yang dibutuhkan homepage. Data name, npm, study_program, bio, dll dimasukkan langsung ke context. Data yang sudah disiapkan view lalu akan dikirim ke templates/index.html. Setelah index.html selesai dirender dengan data dari context, Django akan mengirim HTML ke browser. Browser lalu load CSS dari static file, gambar, JavaScript untuk menu, audio player, dll. Terakhir, user dapat melihat homepage portofolio yang berisi profil, skills, project, dan discography.

2. Data untuk section portfolio, seperti Project, DiscographyEntry, dan Experience lebih baik disimpan di model daripada ditulis langsung di template karena model dapat mengelola data secara terstruktur di database. Jika data ditulis langsung di template, setiap kali saya ingin menambahkan pengalaman baru atau update deskripsi project, saya harus mengubah isi HTML secara manual. Cara tersebut tidak efisien dan berpotensi menghasilkan duplikasi kode, terutama karena setiap kartu experience atau project punya struktur HTML yang mirip. Selain itu dengan model, saya bisa menambahkan atau update data lewat Django Admin page tanpa harus mengedit template.

3. Makemigrations digunakan untuk mendeteksi update pada model dan membuat file migration baru. File migration berisi instruksi perubahan struktur database, tapi perintah ini tidak mengubah database secara langsung. Migrate digunakan untuk menjalankan migration yang sudah dibuat ke database. Setelah perintah ini dijalankan, struktur tabel pada database akan dibuat atau diupdate.

## AI DISCLOSURE
Dalam pengerjaan Tugas 2, saya menggunakan GPT-5.6-terra terutama dalam proses debugging, proses-proses repetitif, dan minta penjelasan tentang konsep dan cara kerja MVT.

Detail section yang dibantu AI:
1. Isi seed_portfolio EXPERIENCES, saya ekstrak data pengalaman saya dari LinkedIn dan lempar ke LLM untuk generate EXPERIENCES yang sudah terstruktur dan rapih.
2. Refactor Project dan Discography ke MVT dipandu AI.



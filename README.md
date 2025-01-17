
# Petualangan Si Pintar

**Petualangan Si Pintar** adalah game edukasi berbasis Kivy yang menawarkan beberapa level tantangan, mulai dari puzzle gambar hingga pertarungan boss dengan pertanyaan pilihan ganda. Game ini memberikan hint saat jawaban salah dan menampilkan popup khusus ketika pemain menang atau kalah.

## Daftar Isi
- [Fitur Utama](#fitur-utama)
- [Struktur Proyek](#struktur-proyek)
- [Instalasi](#instalasi)
- [Penggunaan](#penggunaan)
- [Potongan Kode Penting](#potongan-kode-penting)
- [Lisensi](#lisensi)

## Fitur Utama
- **Level 1 - Puzzle:** Susun potongan gambar untuk menyelesaikan puzzle.
- **Tombol Tampilkan Solusi:** Menggunakan tombol gambar `solusi.png` untuk menampilkan solusi puzzle.
- **Level 2 - Kuis Pilihan Ganda:** Jawab pertanyaan dengan hint yang muncul jika salah.
- **Level 3 - Boss Battle:** Jawab rangkaian pertanyaan untuk mengalahkan boss. Jika gagal atau waktunya habis, muncul popup kekalahan.
- **Popup Menang/Kalah:** Menampilkan gambar dan memutar suara khusus saat menang (`win.png`, `win.wav`) atau kalah (`lose.png`, `lose.wav`).
- **Hint dengan Latar Belakang:** Teks hint ditampilkan di atas latar belakang `hint_bg.png`.

## Struktur Proyek

```
PetualanganSiPintar/
├── assets/
│   ├── button_start_normal.png
│   ├── button_start_pressed.png
│   ├── ... (aset lainnya)
│   ├── hint_bg.png
│   ├── solusi.png
│   ├── win.png
│   ├── lose.png
│   ├── click.wav
│   ├── correct.wav
│   ├── incorrect.wav
│   ├── win.wav
│   ├── lose.wav
│   └── bg_music.mp3
├── questions.json
├── progress.json         # Dibuat secara otomatis saat permainan berjalan
├── settings.json         # Dibuat secara otomatis saat pengaturan disimpan
├── main.py
└── petualangan.kv
```

## Instalasi

1. **Prasyarat:**
   - Python 3.x
   - Kivy (versi 2.1.0 atau lebih baru)

2. **Langkah-langkah:**
   - Clone atau unduh repository ini.
   - Install dependensi Kivy:
     ```bash
     pip install kivy
     ```
   - Pastikan semua aset (gambar dan suara) berada di folder `assets/`.

## Penggunaan

Jalankan aplikasi dengan perintah:
```bash
python main.py
```
Navigasikan melalui menu utama untuk memulai atau melanjutkan permainan. Gunakan tombol pada layar untuk berinteraksi dengan game. Di Level 1, gunakan tombol berbasis gambar "Tampilkan Solusi" untuk melihat solusi puzzle jika diperlukan.

## Potongan Kode Penting

### Definisi `<HintLabel>`
Menampilkan teks hint di atas latar belakang:
```kv
<HintLabel@Label>:
    text: ""
    font_size: '16sp'
    font_name: 'assets/fun_font.ttf'
    color: 1,0,0,1
    size_hint: None, None
    halign: 'center'
    valign: 'middle'
    text_size: self.size
    canvas.before:
        Color:
            rgba: 1,1,1,0.8
        Rectangle:
            pos: self.pos
            size: self.size
            source: 'assets/hint_bg.png'
```

### Tombol "Tampilkan Solusi"
Tombol berbasis gambar untuk menampilkan solusi puzzle:
```kv
<ButtonSolusi@ButtonBehavior+Image>:
    source: 'assets/solusi.png'
    allow_stretch: True
    keep_ratio: False
    size_hint: None, None
    size: dp(150), dp(50)
    on_release: app.show_puzzle_solution()
```

### Metode `show_puzzle_solution()`
Menyelesaikan puzzle dan memperbarui tampilan:
```python
def show_puzzle_solution(self):
    self.puzzle_order = self.puzzle_tiles[:]
    self.empty_index = self.puzzle_order.index("assets/puzzle_empty.png")
    self.refresh_puzzle_grid()
    self.play_click_sound()
```

### Popup Menang/Kalah
Menampilkan popup dengan gambar dan suara saat menang atau kalah:
```python
def show_win_popup(self):
    from kivy.uix.popup import Popup
    from kivy.uix.image import Image
    popup = Popup(title='Selamat!',
                  content=Image(source='assets/win.png'),
                  size_hint=(None, None),
                  size=(400, 400))
    popup.open()
    if self.win_sound:
        self.win_sound.play()

def show_lose_popup(self):
    from kivy.uix.popup import Popup
    from kivy.uix.image import Image
    popup = Popup(title='Maaf!',
                  content=Image(source='assets/lose.png'),
                  size_hint=(None, None),
                  size=(400, 400))
    popup.open()
    if self.lose_sound:
        self.lose_sound.play()
```

### Logika Kekalahan Level 3 di `load_boss_question()`
Memeriksa apakah boss belum dikalahkan dan semua pertanyaan habis:
```python
if self.current_question_index >= len(self.questions_data['level3']):
    if boss_health_bar.value > 0:
        print("Boss belum kalah. Anda kalah!")
        self.show_lose_popup()
    self.go_to_main_menu()
    return
```

## Lisensi

Deskripsikan lisensi di sini jika ada. Misalnya:
```
MIT License
```

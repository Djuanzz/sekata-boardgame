# Sekata - Permainan Papan Online Multiplayer

Sekata adalah permainan papan kata berbasis potongan kata yang dimainkan secara online dengan multiple pemain. Pemain berlomba untuk menyambung potongan kata menjadi kata yang valid dalam Bahasa Indonesia.

## 📋 Daftar Isi

- [Deskripsi Permainan](#deskripsi-permainan)
- [Fitur](#fitur)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Persyaratan Sistem](#persyaratan-sistem)
- [Instalasi dan Setup](#instalasi-dan-setup)
- [Cara Menjalankan](#cara-menjalankan)
- [Cara Bermain](#cara-bermain)
- [Struktur Proyek](#struktur-proyek)
- [API Endpoints](#api-endpoints)
- [Pengembangan](#pengembangan)
- [Troubleshooting](#troubleshooting)

## 🎮 Deskripsi Permainan

Sekata adalah permainan kata yang menantang dimana pemain menggunakan potongan kata (fragmen) untuk membentuk kata-kata yang valid. Setiap pemain memiliki kartu berisi potongan kata di tangan mereka dan harus menyambungkan potongan kata tersebut dengan kartu yang ada di meja untuk membentuk kata yang ada dalam kamus Bahasa Indonesia.

### Tujuan Permainan

- Habiskan semua kartu di tangan Anda terlebih dahulu
- Bentuk kata-kata valid untuk mendapatkan poin
- Gunakan strategi dengan kartu helper untuk keuntungan tambahan

## ✨ Fitur

### Fitur Utama

- **Multiplayer Online**: Mendukung beberapa pemain secara bersamaan
- **Real-time Updates**: Status permainan diperbarui secara real-time
- **Kamus Bahasa Indonesia**: Validasi kata menggunakan kamus lengkap
- **Kartu Helper**: Kartu khusus yang memberikan keuntungan strategis
- **Sistem Skor**: Perhitungan skor berdasarkan panjang kata yang terbentuk

### Interface

- **Web Client**: Interface HTML/CSS/JavaScript yang responsif
- **Desktop Client**: Aplikasi desktop menggunakan Pygame
- **Cross-platform**: Dapat dijalankan di Windows, macOS, dan Linux

## 🏗️ Arsitektur Sistem

Sistem Sekata menggunakan arsitektur client-server dengan komponen berikut:

```
┌─────────────────┐    HTTP/Socket    ┌─────────────────┐
│   Web Client    │◄─────────────────►│                 │
│  (HTML/JS/CSS)  │                   │                 │
└─────────────────┘                   │   HTTP Server   │
                                      │   (Threading)   │
┌─────────────────┐    HTTP/Socket    │                 │
│ Desktop Client  │◄─────────────────►│                 │
│   (Pygame)      │                   │                 │
└─────────────────┘                   └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │   Game Logic    │
                                    │   & Models      │
                                    └─────────────────┘
```

### Komponen Utama

1. **HTTP Server** (`server_thread_http.py`, `http.py`): Server multithreaded yang menangani request HTTP
2. **Game Logic** (`models.py`): Logika permainan, pemain, dan deck kartu
3. **Utilities** (`utils.py`): Validasi kata dan utilitas lainnya
4. **Web Client** (`index.html`, `static/js/`): Interface web browser
5. **Desktop Client** (`pygame_client/`): Aplikasi desktop dengan Pygame

## 💻 Persyaratan Sistem

### Server Requirements

- Python 3.8 atau lebih baru
- Sistem operasi: Windows, macOS, atau Linux
- RAM minimal: 512 MB
- Storage: 100 MB ruang kosong

### Client Requirements

#### Web Client

- Browser modern (Chrome, Firefox, Safari, Edge)
- JavaScript enabled

#### Desktop Client (Pygame)

- Python 3.8 atau lebih baru
- Pygame library
- Resolusi layar minimal: 900x750 pixels

## 🔧 Instalasi dan Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd sekata-boardgame
```

### 2. Setup Server

Tidak ada dependencies khusus yang diperlukan untuk server karena menggunakan library bawaan Python.

### 3. Setup Desktop Client (Opsional)

Jika ingin menjalankan desktop client:

```bash
pip install pygame
```

### 4. Persiapan Kamus

Pastikan file `static/dictionary.txt` berisi kata-kata Bahasa Indonesia (satu kata per baris). Jika file tidak ada, sistem akan menggunakan kamus fallback.

## 🚀 Cara Menjalankan

### Menjalankan Server

```bash
python server_thread_http.py
```

Server akan berjalan di `http://localhost:8000`

### Mengakses Game

#### Via Web Browser

1. Buka browser
2. Navigasi ke `http://localhost:8000`
3. Masukkan nama pemain
4. Buat game baru atau bergabung dengan game yang ada

#### Via Desktop Client

```bash
cd pygame_client
python main.py
```

## 🎯 Cara Bermain

### Setup Awal

1. **Buat Game**: Pemain pertama membuat game baru dan mendapat Game ID
2. **Bergabung**: Pemain lain bergabung menggunakan Game ID
3. **Mulai**: Host memulai permainan setelah cukup pemain bergabung (minimal 2 pemain)

### Gameplay

1. **Kartu Awal**: Setiap pemain mendapat 7 kartu potongan kata
2. **Kartu Meja**: Satu kartu potongan kata diletakkan di meja sebagai titik awal
3. **Giliran**: Pemain bergantian bermain

### Dalam Setiap Giliran

1. **Pilih Kartu**: Pilih kartu dari tangan Anda
2. **Sambung Kata**: Sambungkan di depan atau belakang kartu meja
3. **Validasi**: Kata yang terbentuk harus ada dalam kamus
4. **Kirim**: Submit kata yang valid untuk mendapat poin
5. **Kartu Helper**: Opsional menggunakan kartu helper untuk keuntungan tambahan

### Aksi Alternatif

- **Check**: Lewati giliran jika tidak bisa membentuk kata
- **Reset**: Batalkan pilihan kartu dalam giliran

### Menang

- Pemain yang menghabiskan semua kartunya terlebih dahulu menang
- Atau pemain dengan skor tertinggi jika deck habis

## 📁 Struktur Proyek

```
sekata-boardgame/
├── README.md                 # Dokumentasi proyek
├── server_thread_http.py     # Server utama
├── http.py                   # HTTP request handler
├── models.py                 # Model game dan pemain
├── utils.py                  # Utilitas validasi kata
├── index.html               # Interface web utama
├── static/                  # Asset web
│   ├── css/
│   │   └── style.css        # Styling web
│   ├── js/
│   │   ├── main.js          # Logic utama web client
│   │   ├── api.js           # API calls
│   │   ├── state.js         # State management
│   │   └── ui.js            # UI rendering
│   └── dictionary.txt       # Kamus Bahasa Indonesia
├── pygame_client/           # Desktop client
│   ├── main.py              # Entry point desktop client
│   ├── game_state.py        # State management
│   ├── network_client.py    # Network communication
│   └── ui_elements.py       # UI components
└── dataset/                 # Data preprocessing
    ├── cards/
    └── words/
```

## 🌐 API Endpoints

### Game Management

- `POST /create_game` - Membuat game baru
- `POST /join_game/{game_id}` - Bergabung ke game
- `POST /start_game/{game_id}` - Memulai permainan (host only)
- `GET /game_status/{game_id}` - Mendapat status game

### Gameplay

- `POST /submit_turn/{game_id}` - Submit giliran dengan kata
- `POST /check_turn/{game_id}` - Lewati giliran

### Static Files

- `GET /` - Halaman utama
- `GET /static/*` - File statis (CSS, JS, images)

### Request/Response Format

Semua endpoint menggunakan JSON format:

```json
{
  "success": true/false,
  "message": "Pesan informasi",
  "data": {}, // Data spesifik endpoint
  "game_id": "ABC123" // Untuk response create_game
}
```

## 🛠️ Pengembangan

### Menambah Kartu Baru

Edit file `models.py` di bagian `POTONGAN_KATA`:

```python
POTONGAN_KATA = [
    "KU", "RU", "MA", "AH", "TA", "BU", "KI", "LIT",
    # Tambahkan potongan kata baru di sini
]
```

### Menambah Kata ke Kamus

Tambahkan kata baru ke file `static/dictionary.txt` (satu kata per baris, uppercase).

### Modifikasi Aturan Skor

Edit fungsi `calculate_score_for_word()` di `utils.py`:

```python
def calculate_score_for_word(formed_word):
    # Contoh: skor berdasarkan panjang kata
    return len(formed_word)
```

### Kustomisasi UI

- **Web**: Edit file dalam folder `static/`
- **Desktop**: Edit file dalam folder `pygame_client/`

## 🔧 Troubleshooting

### Masalah Umum

#### Server tidak bisa dijalankan

```
Error: Address already in use
```

**Solusi**: Port 8000 sedang digunakan. Ganti port di `server_thread_http.py` atau hentikan proses yang menggunakan port tersebut.

#### Client tidak bisa connect

```
Error: Connection refused
```

**Solusi**:

1. Pastikan server sedang berjalan
2. Periksa firewall settings
3. Gunakan IP address yang benar

#### Kata tidak divalidasi

```
Error: Kata 'xxx' tidak ada dalam kamus
```

**Solusi**:

1. Periksa file `static/dictionary.txt`
2. Pastikan kata ditulis dalam uppercase
3. Tambahkan kata ke kamus jika diperlukan

#### Pygame client error

```
Error: No module named 'pygame'
```

**Solusi**: Install pygame dengan `pip install pygame`

### Log dan Debug

Server mencatat aktivitas di console. Untuk debug lebih detail, ubah level logging di `server_thread_http.py`:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

Jika game terasa lambat:

1. Kurangi interval polling di client (default: 2 detik)
2. Optimalkan ukuran kamus
3. Batasi jumlah concurrent players

## 📝 Lisensi

Proyek ini dibuat untuk tujuan edukatif dalam mata kuliah Pemrograman Jaringan.

## 🤝 Kontribusi

Untuk berkontribusi:

1. Fork repository
2. Buat feature branch
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request

## 📞 Support

Jika mengalami masalah atau memiliki pertanyaan, silakan buat issue di repository atau hubungi maintainer proyek.

---

**Selamat bermain Sekata! 🎉**

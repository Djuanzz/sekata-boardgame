# Sekata - Permainan Papan Online Multiplayer Cross-Platform

Sekata adalah permainan papan kata berbasis potongan kata yang dimainkan secara online dengan multiple pemain. Pemain berlomba untuk menyambung potongan kata menjadi kata yang valid dalam Bahasa Indonesia. Game ini mendukung arsitektur terdistribusi dengan load balancer dan dapat dijalankan di berbagai platform (Windows, macOS, Linux).

## 📋 Daftar Isi

- [Deskripsi Permainan](#deskripsi-permainan)
- [Fitur](#fitur)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Load Balancer & High Availability](#load-balancer--high-availability)
- [Cross-Platform Support](#cross-platform-support)
- [Persyaratan Sistem](#persyaratan-sistem)
- [Instalasi dan Setup](#instalasi-dan-setup)
- [Cara Menjalankan](#cara-menjalankan)
- [Konfigurasi Load Balancer](#konfigurasi-load-balancer)
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
- **Load Balancer**: Distribusi beban otomatis untuk scalability tinggi
- **High Availability**: Dukungan multiple backend servers
- **Cross-Platform**: Kompatibel dengan Windows, macOS, dan Linux
- **Multi-Client**: Web browser dan aplikasi desktop native
- **Kamus Bahasa Indonesia**: Validasi kata menggunakan kamus lengkap
- **Kartu Helper**: Kartu khusus yang memberikan keuntungan strategis
- **Sistem Skor**: Perhitungan skor berdasarkan panjang kata yang terbentuk
- **Session Persistence**: Game state yang persistent dengan sticky sessions

### Interface

- **Web Client**: Interface HTML/CSS/JavaScript yang responsif
- **Desktop Client**: Aplikasi desktop menggunakan Pygame
- **Cross-platform**: Dapat dijalankan di Windows, macOS, dan Linux
- **Responsive Design**: Otomatis menyesuaikan berbagai ukuran layar

## 🏗️ Arsitektur Sistem

Sistem Sekata menggunakan arsitektur client-server terdistribusi dengan load balancer untuk scalability dan high availability:

```
┌─────────────────┐                    ┌─────────────────┐
│   Web Client    │                    │                 │
│  (HTML/JS/CSS)  │◄──────────────────►│                 │
└─────────────────┘                    │                 │
                                       │  Load Balancer  │
┌─────────────────┐     HTTP/Socket    │   (Port 6666)   │
│ Desktop Client  │◄──────────────────►│                 │
│   (Pygame)      │                    │                 │
└─────────────────┘                    └─────────┬───────┘
                                                 │
                            ┌────────────────────┼────────────────────┐
                            │                    │                    │
                            ▼                    ▼                    ▼
                   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
                   │   HTTP Server   │  │   HTTP Server   │  │   HTTP Server   │
                   │   (Port 8000)   │  │   (Port 8001)   │  │   (Port 800X)   │
                   └─────────┬───────┘  └─────────┬───────┘  └─────────┬───────┘
                             │                    │                    │
                             └────────────────────┼────────────────────┘
                                                  │
                                                  ▼
                                        ┌─────────────────┐
                                        │   Game Logic    │
                                        │   & Models      │
                                        │  (Shared State) │
                                        └─────────────────┘
```

### Komponen Utama

1. **Load Balancer** (`load_balancer.py`): Distribusi permintaan ke multiple backend servers
2. **HTTP Servers** (`server_thread_http.py`, `http.py`): Multiple backend servers dengan session sticky
3. **Game Logic** (`models.py`): Logika permainan, pemain, dan deck kartu
4. **Utilities** (`utils.py`): Validasi kata dan utilitas lainnya
5. **Web Client** (`index.html`, `static/js/`): Interface web browser
6. **Desktop Client** (`pygame_client/`): Aplikasi desktop dengan Pygame

## ⚖️ Load Balancer & High Availability

### Fitur Load Balancer

- **Round-Robin Distribution**: Distribusi permintaan secara merata
- **Sticky Sessions**: Game-specific routing untuk konsistensi state
- **Automatic Failover**: Pengalihan otomatis jika server down
- **Health Monitoring**: Pemantauan status backend servers
- **Game State Persistence**: Menjaga konsistensi state game

### Konfigurasi Default

- **Load Balancer Port**: 6666
- **Backend Servers**: Dapat dikonfigurasi multiple servers
- **Session Affinity**: Berdasarkan Game ID untuk consistency

### Keuntungan Arsitektur

1. **Scalability**: Mudah menambah backend servers sesuai kebutuhan
2. **Reliability**: Tidak ada single point of failure
3. **Performance**: Distribusi beban yang optimal
4. **Maintenance**: Rolling updates tanpa downtime

## 🌐 Cross-Platform Support

### Platform yang Didukung

#### Server Side

- **Windows** (Windows 10/11, Windows Server 2016+)
- **macOS** (macOS 10.14+, Big Sur, Monterey, Ventura)
- **Linux** (Ubuntu 18.04+, CentOS 7+, Debian 9+, Fedora 30+)

#### Client Side

##### Web Client

- **Windows**: Chrome 80+, Firefox 75+, Edge 80+
- **macOS**: Safari 13+, Chrome 80+, Firefox 75+
- **Linux**: Chrome 80+, Firefox 75+, Chromium 80+
- **Mobile**: iOS Safari 13+, Android Chrome 80+

##### Desktop Client (Pygame)

- **Windows**: Windows 7+ dengan Python 3.8+
- **macOS**: macOS 10.13+ dengan Python 3.8+
- **Linux**: Distribusi utama dengan Python 3.8+ dan X11/Wayland

### Kompatibilitas Network

- **IPv4/IPv6**: Dukungan dual-stack
- **Firewall**: Kompatibel dengan NAT dan corporate firewall
- **Proxy**: Dukungan HTTP proxy untuk enterprise environment
- **Cloud**: Dapat di-deploy di AWS, GCP, Azure, atau cloud provider lainnya

## 💻 Persyaratan Sistem

### Server Requirements

- **Python**: 3.8 atau lebih baru
- **Operating System**:
  - Windows 10/11 atau Windows Server 2016+
  - macOS 10.14+ (Mojave, Big Sur, Monterey, Ventura)
  - Linux: Ubuntu 18.04+, CentOS 7+, Debian 9+, Fedora 30+
- **RAM**: Minimal 512 MB (1 GB recommended untuk production)
- **Storage**: 100 MB ruang kosong (500 MB untuk multiple servers)
- **Network**: Port 8000-8010 dan 6969 untuk load balancer
- **Python Modules**: Built-in libraries only (http.server, threading, json, requests untuk load balancer)

### Client Requirements

#### Web Client

- **Browser Modern**:
  - Chrome/Chromium 80+
  - Firefox 75+
  - Safari 13+ (macOS/iOS)
  - Microsoft Edge 80+
- **JavaScript**: Harus aktif
- **Network**: Akses HTTP ke server (port 6969 untuk load balancer atau 8000+ untuk direct)
- **Resolution**: Minimal 800x600, optimal 1024x768+

#### Desktop Client (Pygame)

- **Python**: 3.8+ dengan pip
- **Pygame**: Library pygame (`pip install pygame`)
- **Operating System**:
  - Windows 7+ (dengan Visual C++ Redistributable)
  - macOS 10.13+ (High Sierra atau lebih baru)
  - Linux dengan X11 atau Wayland display server
- **Hardware**:
  - Resolusi layar minimal: 900x750 pixels
  - RAM: 256 MB untuk client
  - Graphics: Dukungan SDL2 (biasanya built-in)

### Network Requirements

- **Bandwidth**: Minimal 56 Kbps (broadband recommended)
- **Latency**: < 500ms untuk pengalaman optimal
- **Firewall**: Akses HTTP/HTTPS untuk ports yang dikonfigurasi
- **Proxy**: Dukungan HTTP proxy (jika diperlukan)

## 🔧 Instalasi dan Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd sekata-boardgame
```

### 2. Setup Server

#### Single Server Mode (Development)

Tidak ada dependencies khusus yang diperlukan untuk server karena menggunakan library bawaan Python.

#### Multi-Server Mode dengan Load Balancer (Production)

Untuk setup production dengan load balancer, install requests untuk load balancer:

```bash
pip install requests
```

### 3. Setup Desktop Client (Opsional)

Jika ingin menjalankan desktop client:

```bash
pip install pygame
```

### 4. Persiapan Kamus

Pastikan file `static/dictionary.txt` berisi kata-kata Bahasa Indonesia (satu kata per baris). Jika file tidak ada, sistem akan menggunakan kamus fallback.

### 5. Konfigurasi Load Balancer (Production)

Edit file `load_balancer.py` untuk menyesuaikan backend servers:

```python
BACKEND_SERVERS = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
    "http://192.168.1.100:8000",  # Server lain di network
    # Tambahkan server lain sesuai kebutuhan
]
LOAD_BALANCER_PORT = 6969
```

## 🚀 Cara Menjalankan

### Mode Development (Single Server)

#### Menjalankan Server Tunggal

```bash
python server_thread_http.py
```

Server akan berjalan di `http://localhost:8000`

### Mode Production (Load Balancer + Multiple Servers)

#### 1. Jalankan Multiple Backend Servers

Terminal 1:

```bash
python server_thread_http.py --port 8000
```

Terminal 2:

```bash
python server_thread_http.py --port 8001
```

Terminal 3 (dan seterusnya):

```bash
python server_thread_http.py --port 8002
```

#### 2. Jalankan Load Balancer

Terminal terpisah:

```bash
python load_balancer.py
```

Load Balancer akan berjalan di `http://localhost:6969`

### Mengakses Game

#### Via Web Browser (Recommended)

**Development Mode:**

1. Buka browser
2. Navigasi ke `http://localhost:8000`
3. Masukkan nama pemain
4. Buat game baru atau bergabung dengan game yang ada

**Production Mode:**

1. Buka browser
2. Navigasi ke `http://localhost:6969` (Load Balancer)
3. Masukkan nama pemain
4. Buat game baru atau bergabung dengan game yang ada

#### Via Desktop Client

```bash
cd pygame_client
python main.py
```

**Catatan untuk Desktop Client:**

- Untuk development: Client akan connect ke `localhost:8000`
- Untuk production: Ubah endpoint di `network_client.py` ke `localhost:6969`

## ⚙️ Konfigurasi Load Balancer

### Pengaturan Backend Servers

Edit `load_balancer.py`:

```python
# Konfigurasi server backend
BACKEND_SERVERS = [
    "http://127.0.0.1:8000",     # Server lokal 1
    "http://127.0.0.1:8001",     # Server lokal 2
    "http://192.168.1.100:8000", # Server di network lain
    "http://10.0.0.50:8000",     # Server production
]

# Port load balancer
LOAD_BALANCER_PORT = 6969
```

### Load Balancing Strategy

- **Round-Robin**: Requests didistribusikan secara berurutan
- **Sticky Sessions**: Game sessions tetap di server yang sama
- **Automatic Failover**: Jika server tidak responsif, requests dialihkan

### Monitoring dan Logging

Load balancer mencatat semua aktivitas:

- Game creation dan server assignment
- Session routing
- Server health status
- Error handling

### High Availability Setup

Untuk setup production yang robust:

1. **Multiple Servers**: Minimum 2-3 backend servers
2. **Health Checks**: Load balancer melakukan health monitoring
3. **Graceful Degradation**: Jika server down, sessions dialihkan
4. **Logging**: Full logging untuk debugging dan monitoring

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
├── server_thread_http.py     # Server backend utama
├── load_balancer.py          # Load balancer untuk production
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
├── pygame_client/           # Desktop client (Cross-platform)
│   ├── main.py              # Entry point desktop client
│   ├── game_state.py        # State management
│   ├── network_client.py    # Network communication
│   └── ui_elements.py       # UI components
├── dataset/                 # Data preprocessing
│   ├── cards/
│   │   ├── preprocess.py    # Preprocessing kartu
│   │   └── top_word_connections.csv
│   └── words/
│       ├── indonesian-words.csv
│       ├── preprocess.py    # Preprocessing kata
│       └── processed_indonesian_words_max5.csv
└── example/                 # Contoh implementasi
    └── pac.py               # Contoh protocol
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

**Solusi**: Port sedang digunakan. Ganti port atau hentikan proses yang menggunakan port tersebut.

**Windows:**

```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**macOS/Linux:**

```bash
lsof -ti:8000 | xargs kill -9
```

#### Load Balancer connection issues

```
Error: Service Unavailable
```

**Solusi**:

1. Pastikan semua backend servers sedang berjalan
2. Periksa konfigurasi `BACKEND_SERVERS` di `load_balancer.py`
3. Pastikan tidak ada conflict dengan local firewall

#### Client tidak bisa connect

```
Error: Connection refused
```

**Solusi**:

1. Pastikan server/load balancer sedang berjalan
2. Periksa firewall settings (Windows Defender, iptables, dll)
3. Gunakan IP address yang benar
4. Untuk cross-platform: pastikan port forwarding jika melalui NAT

#### Cross-platform specific issues

**Windows:**

- Pastikan Windows Defender tidak memblokir Python
- Install Visual C++ Redistributable untuk Pygame

**macOS:**

- Izinkan Python di Security & Privacy settings
- Install Xcode Command Line Tools jika diperlukan

**Linux:**

- Install SDL2 development libraries:

  ```bash
  # Ubuntu/Debian
  sudo apt install libsdl2-dev

  # CentOS/RHEL
  sudo yum install SDL2-devel
  ```

#### Kata tidak divalidasi

```
Error: Kata 'xxx' tidak ada dalam kamus
```

**Solusi**:

1. Periksa file `static/dictionary.txt`
2. Pastikan kata ditulis dalam uppercase
3. Tambahkan kata ke kamus jika diperlukan
4. Periksa encoding file (harus UTF-8)

#### Pygame client error

```
Error: No module named 'pygame'
```

**Solusi**:

```bash
pip install pygame
```

**Jika masih error di Linux:**

```bash
sudo apt install python3-pygame
```

#### Load Balancer tidak mendistribusikan beban

**Solusi**:

1. Periksa log load balancer untuk memastikan semua server terdeteksi
2. Test manual ke masing-masing backend server
3. Pastikan sticky session berfungsi untuk game consistency

### Performance Optimization

#### Untuk High Load:

1. **Increase Backend Servers**: Tambah server di `BACKEND_SERVERS`
2. **Adjust Polling**: Kurangi interval polling di client
3. **Optimize Dictionary**: Gunakan dictionary yang dioptimasi
4. **Connection Pooling**: Implementasi connection reuse di client

#### Monitoring Production:

```bash
# Monitor server resources
htop  # Linux/macOS
Get-Process python | Sort-Object CPU -Descending  # Windows PowerShell

# Monitor port usage
netstat -tulpn | grep :6969  # Linux
netstat -an | findstr :6969  # Windows
```

### Load Balancer Troubleshooting

#### Debug Mode:

Tambahkan logging detail di `load_balancer.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Health Check Manual:

Test backend servers secara manual:

```bash
curl http://localhost:8000/
curl http://localhost:8001/
```

#### Session Affinity Issues:

Jika game state tidak konsisten:

1. Periksa game ID extraction di `get_target_server()`
2. Pastikan regex pattern sesuai dengan format Game ID
3. Verify sticky session mapping di logs

### Log dan Debug

#### Server Logging:

Server mencatat aktivitas di console. Untuk debug lebih detail:

```python
# Di server_thread_http.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Load Balancer Logging:

Load balancer mencatat semua routing decisions:

```python
# Di load_balancer.py - sudah ada built-in logging
print(f"STICKY: Meneruskan permintaan game {game_id} ke {server}")
print(f"NEW GAME: Memilih server {server} untuk game baru.")
```

#### Client-Side Debugging:

**Web Client:**

- Buka Developer Tools (F12) di browser
- Check Console tab untuk JavaScript errors
- Check Network tab untuk HTTP request/response

**Desktop Client:**

- Tambahkan debug prints di `pygame_client/network_client.py`
- Monitor console output untuk connection issues

### Deployment Options

#### Local Network:

```python
# Ganti IP di load_balancer.py untuk LAN access
BACKEND_SERVERS = [
    "http://192.168.1.100:8000",
    "http://192.168.1.101:8000",
]
```

#### Cloud Deployment:

- **AWS/GCP/Azure**: Deploy di multiple instances
- **Docker**: Containerize untuk easy deployment
- **Kubernetes**: For enterprise-scale deployment

#### Security Considerations:

- Firewall rules untuk production
- HTTPS untuk secure communication
- Rate limiting untuk prevent abuse

## 📝 Lisensi

Proyek ini dibuat untuk tujuan edukatif dalam mata kuliah Pemrograman Jaringan. Mendukung arsitektur terdistribusi dan cross-platform compatibility.

## 🤝 Kontribusi

Untuk berkontribusi:

1. Fork repository
2. Buat feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

### Area Kontribusi:

- Cross-platform testing dan optimization
- Load balancer improvements
- UI/UX enhancements
- Performance optimizations
- Security enhancements
- Documentation improvements

## � Roadmap

### Short Term:

- [ ] Dockerization untuk easy deployment
- [ ] HTTPS support untuk secure communication
- [ ] Enhanced monitoring dan metrics
- [ ] Mobile web client improvements

### Long Term:

- [ ] WebSocket support untuk real-time communication
- [ ] Database persistence untuk game history
- [ ] Tournament mode
- [ ] AI opponent
- [ ] Microservices architecture

## �📞 Support

Jika mengalami masalah atau memiliki pertanyaan:

1. **Issues**: Buat issue di repository untuk bug reports
2. **Documentation**: Periksa README dan inline comments
3. **Community**: Diskusi di repository discussions
4. **Email**: Hubungi maintainer proyek

### Supported Platforms:

- ✅ Windows 10/11
- ✅ macOS Big Sur+
- ✅ Ubuntu 18.04+
- ✅ CentOS 7+
- ✅ Debian 9+

---

**Selamat bermain Sekata di platform favorit Anda! 🎉🖥️📱**

_Game yang mendukung cross-platform gaming dengan arsitektur scalable untuk pengalaman multiplayer yang optimal._

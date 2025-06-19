import os
from collections import Counter
import csv # Modul untuk bekerja dengan file CSV

def analyze_and_save_word_ends_to_csv(input_file_path, output_csv_path, top_n=75):
    """
    Menganalisis frekuensi dua huruf awalan dan akhiran dari daftar kata,
    dan menyimpan top_n ke dalam file CSV.

    Args:
        input_file_path (str): Path ke file CSV hasil preprocessing 
                               (satu kata per baris, sudah bersih dan kapital).
        output_csv_path (str): Path untuk menyimpan file CSV hasil analisis.
        top_n (int): Jumlah pasangan huruf teratas yang ingin dianalisis dan disimpan.
    """
    if not os.path.exists(input_file_path):
        print(f"Error: File input '{input_file_path}' tidak ditemukan.")
        print("Pastikan file hasil preprocessing sebelumnya sudah ada di path yang benar.")
        return

    prefix_counts = Counter()
    suffix_counts = Counter()
    
    words_processed_for_analysis = 0
    words_too_short = 0

    print(f"Mulai menganalisis file: {input_file_path}")
    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            for line_number, line in enumerate(infile, 1):
                word = line.strip()

                if not word:
                    continue

                if len(word) >= 2:
                    prefix = word[:2]
                    suffix = word[-2:]
                    
                    prefix_counts[prefix] += 1
                    suffix_counts[suffix] += 1
                    words_processed_for_analysis +=1
                else:
                    words_too_short +=1
                
                if line_number % 50000 == 0: # Update setiap 50rb baris, sesuaikan jika perlu
                    print(f"Telah memproses {line_number} baris untuk analisis...")

    except Exception as e:
        print(f"Terjadi error saat membaca atau memproses file input: {e}")
        return

    print(f"\n--- Analisis Selesai ---")
    print(f"Total kata yang dianalisis (panjang >= 2 huruf): {words_processed_for_analysis}")
    print(f"Total kata yang terlalu pendek (panjang < 2 huruf) dan dilewati: {words_too_short}")

    # Mengambil top_n awalan dan akhiran yang paling umum
    # most_common mengembalikan list of tuples: [('AB', count), ('CD', count), ...]
    top_prefixes_with_counts = prefix_counts.most_common(top_n)
    top_suffixes_with_counts = suffix_counts.most_common(top_n)

    # Ekstrak hanya pasangan hurufnya saja untuk disimpan ke CSV
    top_prefix_strings = [item[0] for item in top_prefixes_with_counts]
    top_suffix_strings = [item[0] for item in top_suffixes_with_counts]

    # Menulis ke file CSV
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['alf_awal', 'alf_akhir']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader() # Menulis header

            # Tentukan berapa banyak baris yang akan ditulis (maksimum dari panjang kedua list)
            # Kita akan menulis sebanyak top_n baris, mengisi dengan string kosong jika salah satu list lebih pendek
            num_rows_to_write = top_n 

            for i in range(num_rows_to_write):
                awal = top_prefix_strings[i] if i < len(top_prefix_strings) else ""
                akhir = top_suffix_strings[i] if i < len(top_suffix_strings) else ""
                
                # Hanya tulis baris jika setidaknya salah satu (awal atau akhir) tidak kosong
                # Atau, jika kita ingin tetap top_n baris meskipun isinya kosong semua di akhir:
                writer.writerow({'alf_awal': awal, 'alf_akhir': akhir})
        
        print(f"\n--- Hasil Analisis Disimpan ---")
        print(f"Top {top_n} awalan dan akhiran disimpan ke: '{output_csv_path}'")
        
        # Cetak beberapa contoh untuk verifikasi cepat
        print(f"\n--- Contoh Isi '{output_csv_path}' (beberapa baris pertama) ---")
        with open(output_csv_path, 'r', encoding='utf-8') as f_verify:
            for i, line in enumerate(f_verify):
                if i < 12: # Tampilkan header + 11 baris data
                    print(line.strip())
                else:
                    break
            if i < 1 and not line.strip():
                print("File CSV kosong atau hanya berisi header.")


    except Exception as e:
        print(f"Terjadi error saat menulis file CSV: {e}")


# --- Penggunaan ---
if __name__ == "__main__":
    # Path ke file hasil preprocessing sebelumnya (yang maksimal 5 huruf)
    processed_input_file = "dataset/words/processed_indonesian_words_max5.csv" 
    
    # Path untuk menyimpan file CSV output
    output_analysis_csv = "dataset/cards/top_word_connections.csv"

    # Jika Anda menjalankan ini di Kaggle:
    # processed_input_file = "/kaggle/working/processed_indonesian_words_max5.csv"
    # output_analysis_csv = "/kaggle/working/top_word_connections.csv"

    # Membuat dummy file jika file input tidak ada (untuk pengujian lokal)
    if not os.path.exists(processed_input_file):
        print(f"File '{processed_input_file}' tidak ditemukan. Membuat dummy file untuk demonstrasi...")
        dummy_data = [
            "BUKA", "KATA", "MANA", "SAYA", "BUKU", "SAPU", "PUTA", "PADI", "TADI",
            "MUKA", "LUKA", "LAMA", "KAKA", "BABI", "ABAI", "MAIN", "AYAM", "MAAF",
            "NAGA", "RAGA", "TAPA", "SANA", "SINI", "BALI", "KALI", "PINTU", "INTI",
            "MAU", "APA", "ADA", "INI", "ITU", "KE", "DI", "KU", "SA", "BA", "TA"
        ]
        with open(processed_input_file, 'w', encoding='utf-8') as f_dummy:
            for word in dummy_data:
                f_dummy.write(word + '\n')
        print(f"Dummy file '{processed_input_file}' berhasil dibuat.")

    # Tentukan berapa banyak pasangan teratas yang ingin Anda lihat dan simpan
    jumlah_top_pasangan = 75 # Anda bisa set antara 50-100

    analyze_and_save_word_ends_to_csv(processed_input_file, output_analysis_csv, top_n=jumlah_top_pasangan)
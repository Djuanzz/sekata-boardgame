import os
from collections import Counter # Sangat berguna untuk menghitung frekuensi

def analyze_word_ends(input_file_path, top_n=75):
    if not os.path.exists(input_file_path):
        print(f"Error: File input '{input_file_path}' tidak ditemukan.")
        print("Pastikan file hasil preprocessing sebelumnya sudah ada di path yang benar.")
        return None, None

    prefix_counts = Counter()
    suffix_counts = Counter()
    
    words_processed_for_analysis = 0
    words_too_short = 0

    print(f"Mulai menganalisis file: {input_file_path}")
    try:
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            for line_number, line in enumerate(infile, 1):
                word = line.strip()

                if not word: # Lewati baris kosong jika ada
                    continue

                # Kata harus memiliki minimal 2 huruf untuk memiliki awalan/akhiran 2 huruf
                if len(word) >= 2:
                    prefix = word[:2] # Dua huruf pertama
                    suffix = word[-2:] # Dua huruf terakhir
                    
                    prefix_counts[prefix] += 1
                    suffix_counts[suffix] += 1
                    words_processed_for_analysis +=1
                else:
                    words_too_short +=1
                
                if line_number % 20000 == 0:
                    print(f"Telah memproses {line_number} baris untuk analisis...")

    except Exception as e:
        print(f"Terjadi error saat membaca atau memproses file: {e}")
        return None, None

    print(f"\n--- Analisis Selesai ---")
    print(f"Total kata yang dianalisis (panjang >= 2 huruf): {words_processed_for_analysis}")
    print(f"Total kata yang terlalu pendek (panjang < 2 huruf) dan dilewati: {words_too_short}")

    # Mengambil top_n awalan dan akhiran yang paling umum
    top_prefixes = prefix_counts.most_common(top_n)
    top_suffixes = suffix_counts.most_common(top_n)

    return top_prefixes, top_suffixes

# --- Penggunaan ---
if __name__ == "__main__":
    # Path ke file hasil preprocessing sebelumnya (yang maksimal 5 huruf)
    # Sesuaikan jika Anda menggunakan nama file yang berbeda
    processed_input_file = "dataset/words/processed_indonesian_words_max5.csv" 
    
    # Jika Anda menjalankan ini di Kaggle, pastikan path-nya benar, 
    # misalnya "/kaggle/working/processed_indonesian_words_max5.csv"
    # Untuk pengujian lokal, pastikan file tersebut ada di direktori yang sama
    # atau berikan path absolut/relatif yang benar.

    # Jika file belum ada, kita coba buat dummy file untuk demonstrasi
    if not os.path.exists(processed_input_file):
        print(f"File '{processed_input_file}' tidak ditemukan. Membuat dummy file untuk demonstrasi...")
        dummy_data = [
            "BUKA", "KATA", "MANA", "SAYA", "BUKU", "SAPU", "PUTA",
            "MUKA", "LUKA", "LAMA", "KAKA", "BABI", "ABAI", "MAIN",
            "MAAF", "AYAM", "MAU", "APA", "ADA", "INI", "ITU", "KE", "DI"
        ] # kata < 2 huruf akan diskip
        with open(processed_input_file, 'w', encoding='utf-8') as f_dummy:
            for word in dummy_data:
                f_dummy.write(word + '\n')
        print(f"Dummy file '{processed_input_file}' berhasil dibuat.")


    # Tentukan berapa banyak pasangan teratas yang ingin Anda lihat (antara 50-100)
    jumlah_top_pasangan = 75 

    top_prefixes_list, top_suffixes_list = analyze_word_ends(processed_input_file, top_n=jumlah_top_pasangan)

    if top_prefixes_list and top_suffixes_list:
        print(f"\n--- Top {jumlah_top_pasangan} Pasangan Dua Huruf AWALAN Kata ---")
        for i, (prefix, count) in enumerate(top_prefixes_list):
            print(f"{i+1}. '{prefix}' : {count} kali")

        print(f"\n--- Top {jumlah_top_pasangan} Pasangan Dua Huruf AKHIRAN Kata ---")
        for i, (suffix, count) in enumerate(top_suffixes_list):
            print(f"{i+1}. '{suffix}' : {count} kali")
        
        # Anda bisa menyimpan ini ke file jika mau
        # Contoh menyimpan ke file:
        # with open("top_prefixes.txt", "w", encoding="utf-8") as f_pref:
        #     for prefix, count in top_prefixes_list:
        #         f_pref.write(f"{prefix},{count}\n")
        #
        # with open("top_suffixes.txt", "w", encoding="utf-8") as f_suff:
        #     for suffix, count in top_suffixes_list:
        #         f_suff.write(f"{suffix},{count}\n")
        # print("\nTop prefixes dan suffixes juga disimpan ke file terpisah (jika kode penyimpanan diaktifkan).")
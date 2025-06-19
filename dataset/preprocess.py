import os # Untuk memeriksa apakah file input ada (berguna di lingkungan Kaggle)

def preprocess_kbbi_dataset_max5(input_csv_path, output_csv_path):
    """
    Melakukan preprocessing pada dataset KBBI CSV.
    - Menghapus baris yang mengandung spasi.
    - Menghapus baris yang mengandung karakter non-alfabet.
    - Hanya mengambil kata yang memiliki maksimal 5 huruf.
    - Mengubah semua baris yang lolos menjadi kapital.
    - Output memiliki format yang sama (satu kata/frasa per baris).
    """
    processed_lines = []
    skipped_count = 0
    kept_count = 0
    total_lines_read = 0

    if not os.path.exists(input_csv_path):
        print(f"Error: File input '{input_csv_path}' tidak ditemukan.")
        print("Pastikan path file sudah benar dan dataset tersedia di lingkungan Kaggle.")
        return

    try:
        with open(input_csv_path, 'r', encoding='utf-8') as infile:
            print(f"Membaca file: {input_csv_path}...")
            for line_number, line in enumerate(infile, 1):
                total_lines_read = line_number
                original_word = line.strip() # Menghapus whitespace di awal/akhir

                if not original_word: # Lewati baris kosong
                    skipped_count += 1
                    continue

                # 1. Cek apakah ada spasi di dalam kata/frasa
                if ' ' in original_word:
                    # print(f"Baris {line_number}: '{original_word}' -> Dihapus (mengandung spasi)")
                    skipped_count += 1
                    continue

                # 2. Cek apakah ada karakter non-alfabet
                if not original_word.isalpha():
                    # print(f"Baris {line_number}: '{original_word}' -> Dihapus (mengandung karakter non-alfabet)")
                    skipped_count += 1
                    continue
                
                # 3. Cek apakah panjang kata maksimal 5 huruf
                if len(original_word) > 5:
                    # print(f"Baris {line_number}: '{original_word}' -> Dihapus (lebih dari 5 huruf)")
                    skipped_count += 1
                    continue

                # 4. Jika lolos semua filter, ubah menjadi kapital
                processed_word = original_word.upper()
                processed_lines.append(processed_word)
                kept_count += 1
                # print(f"Baris {line_number}: '{original_word}' -> Diproses menjadi '{processed_word}'")

                if line_number % 50000 == 0: # Memberi update setiap 50.000 baris
                    print(f"Telah memproses {line_number} baris... (Disimpan: {kept_count}, Dilewati: {skipped_count})")


    except FileNotFoundError:
        print(f"Error: File input '{input_csv_path}' tidak ditemukan.")
        return
    except Exception as e:
        print(f"Terjadi error saat membaca file pada baris sekitar {total_lines_read + 1}: {e}")
        return

    try:
        with open(output_csv_path, 'w', encoding='utf-8') as outfile:
            for word in processed_lines:
                outfile.write(word + '\n')

        print(f"\n--- Preprocessing Selesai ---")
        print(f"Total baris dibaca dari input : {total_lines_read}")
        print(f"Total baris disimpan ke output: {kept_count}")
        print(f"Total baris dilewati/dihapus : {skipped_count}")
        print(f"Hasil disimpan di             : '{output_csv_path}'")

    except Exception as e:
        print(f"Terjadi error saat menulis file output: {e}")

# --- Penggunaan Langsung dengan Path Kaggle ---
if __name__ == "__main__":
    # Path input sesuai permintaan
    input_file_path = "/kaggle/input/kbbi-indonesia/indonesian-words.csv"
    
    # Path output (akan disimpan di direktori kerja Kaggle, yaitu /kaggle/working/)
    output_file_path = "processed_indonesian_words_max5.csv" # Nama file output diubah sedikit

    print(f"Memulai preprocessing untuk file: '{input_file_path}'")
    print(f"Output akan disimpan di: '/kaggle/working/{output_file_path}' (jika dijalankan di Kaggle)")
    print("Aturan tambahan: Hanya kata dengan maksimal 5 huruf yang akan diambil.")
    
    preprocess_kbbi_dataset_max5(input_file_path, output_file_path)

    print("\n--- Verifikasi Output (10 baris pertama jika ada) ---")
    if os.path.exists(output_file_path):
        try:
            line_count_output = 0
            with open(output_file_path, 'r', encoding='utf-8') as f_out:
                for i, line_content in enumerate(f_out):
                    if i < 10:
                        print(line_content.strip())
                    line_count_output +=1
            
            if line_count_output == 0:
                 print(f"File '{output_file_path}' kosong setelah preprocessing.")
            elif line_count_output > 0 and line_count_output <=10:
                 print(f"Total {line_count_output} baris dalam file output.")
            elif line_count_output > 10:
                print("... (dan seterusnya jika ada lebih banyak data)")
                print(f"Total {line_count_output} baris dalam file output.")


        except Exception as e:
            print(f"Error saat membaca file output untuk verifikasi: {e}")
    else:
        print(f"File output '{output_file_path}' tidak ditemukan. Mungkin terjadi error saat proses utama.")
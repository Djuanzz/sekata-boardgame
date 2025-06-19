# sekata_game/utils.py

# Asumsi DICTIONARY dimuat di server.py dan diakses sebagai global
# DICTIONARY = set() # Akan dimuat dari file di server.py

def is_word_in_dictionary(word, dictionary_set):
    """
    Memeriksa apakah sebuah kata UTUH ada di kamus.
    Args:
        word (str): Kata yang akan diperiksa (harus uppercase).
        dictionary_set (set): Set kata-kata dari kamus (uppercase).
    Returns:
        bool: True jika kata ada di kamus, False jika tidak.
    """
    return word.upper() in dictionary_set

def validate_word_formation(current_table_card, new_fragment, position, dictionary_set):
    """
    Memvalidasi apakah penambahan potongan kata membentuk kata yang valid.
    Args:
        current_table_card (str): Kartu potongan kata yang ada di meja.
        new_fragment (str): Potongan kata baru dari tangan pemain.
        position (str): 'before' atau 'after' (menyambung sebelum atau sesudah).
        dictionary_set (set): Set kata-kata dari kamus.
    Returns:
        tuple: (bool, str, str) - True/False, pesan, dan kata utuh yang terbentuk (jika valid).
    """
    new_fragment_upper = new_fragment.upper()
    current_table_card_upper = current_table_card.upper()
    
    formed_word = ""
    if position == 'before':
        formed_word = new_fragment_upper + current_table_card_upper
    elif position == 'after':
        formed_word = current_table_card_upper + new_fragment_upper
    else:
        return False, "Posisi penyambungan tidak valid (harus 'before' atau 'after').", ""

    if is_word_in_dictionary(formed_word, dictionary_set):
        return True, "Pembentukan kata valid.", formed_word
    else:
        return False, f"Kata '{formed_word}' tidak ada di kamus.", ""

def calculate_score_for_word(formed_word):
    """
    Menghitung skor berdasarkan kata yang terbentuk.
    Args:
        formed_word (str): Kata utuh yang terbentuk.
    Returns:
        int: Skor yang didapat (misal, berdasarkan panjang kata).
    """
    # Skor sederhana: 1 poin per huruf
    return len(formed_word)
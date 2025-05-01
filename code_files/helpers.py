from config import all_verses ,start_ayah, end_ayah
from api_calls import generate_surah_metadata


import arabic_reshaper
from bidi.algorithm import get_display
import re
import datetime


bismillah_text = "بِسۡمِ ٱللَّهِ ٱلرَّحۡمَـٰنِ ٱلرَّحِیمِ"


def basic_data_check(surah_number):
    try:
        if surah_number > 114:
            print("Invalid Value input for Surah")
            print("Exiting Program...")
            exit()

        surah_meta = generate_surah_metadata()
        num_ayahs = surah_meta['data']['numberOfAyahs']
        surah_name = surah_meta['data']['englishName']

        print(f"Surah {surah_name} consists of {num_ayahs} verses.")

        if all_verses is True:
            first_ayah = 1
            last_ayah = num_ayahs
        else:
            first_ayah = start_ayah
            last_ayah = end_ayah
            if first_ayah < 1 or last_ayah > num_ayahs:
                print("Invalid Value input for verses")
                print("Exiting Program...")
                exit()
        
        print(f"surah_meta: {surah_meta}")
        print(f"first ayah: {first_ayah}")
        print(f"last_ayah: {last_ayah}")

        return surah_meta, first_ayah , last_ayah

    except Exception as e:
        print("Process failed during Basic data check")
        print("Error occured: ",e)
        print("Exiting program...")
        exit()



def find_best_match(log_verses, current_pos):
    # Filter entries with the same start_pos
    candidates = [entry for entry in log_verses if entry['start_pos'] == current_pos]


    # Further filter where token_similarity < 50 or sequence_similarity < 30
    weak_matches = [
        entry for entry in candidates
        if entry['token_similarity_with_the_next_verse'] < 40 and entry['seq_similarity_with_the_next_verse'] < 50
    ]
    if weak_matches:
        # print("Weak matches:", weak_matches)
        best_entry = max(weak_matches, key=lambda x: x['end_pos'])

    if not weak_matches:
        # print("No weak matches available !")
        best_entry = max(
            candidates,
            key=lambda x: (x['token_similarity'], x['sequence_similarity'], x['end_pos'])
        )  

    # Among the weak matches, find the one with the highest end_pos
    

    return best_entry


def fix_arabic_display(text):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text    


def preprocess_text(text):
    try:
        text = re.sub(r'[إأٱآا]', 'ا', text)  # Replace different 'A' forms with 'ا'
        text = re.sub(r'ى', 'ي', text)        # Replace 'ى' with 'ي'
        text = re.sub(r'ؤ', 'و', text)        # Replace 'ؤ' with 'و'
        text = re.sub(r'ة', 'ه', text)        # Replace 'ة' with 'ه'
        
        cleaned_text = re.sub(r'[\u064B-\u0652]', '', text)  # Remove diacritics
        cleaned_text = re.sub(r'[^\u0600-\u06FF\s]', '', cleaned_text)  # Keep only Arabic letters and spaces
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()  # Normalize whitespace
        return cleaned_text
    
    except Exception as e:
        print("Process failed during Preprocessing of verses text")
        print("Error occured: ",e)
        print("Exiting program...")
        exit()



def time_to_seconds(t):
    """Convert 'min: sec' format to total seconds."""
    t = t.replace(' ', '')  # remove spaces
    minutes, seconds = map(int, t.split(':'))
    return minutes * 60 + seconds



def wrap_text(text, max_chars):
    """Wrap text to a specified number of characters per line."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0

    for word in words:
        if current_length + len(word) + len(current_line) <= max_chars:
            current_line.append(word)
            current_length += len(word)
        else:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_length = len(word)
    
    lines.append(" ".join(current_line))
    return lines

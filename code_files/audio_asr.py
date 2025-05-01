import arabic_reshaper
from bidi.algorithm import get_display
from config import surah_number, asr_model
from similarity_testing import  is_similar, min_treshold, similarity_calculator
from helpers import basic_data_check, bismillah_text, find_best_match, preprocess_text#, process_cal
import json
from pydub import AudioSegment, silence




def detect_silence(sound, silence_threshold=-50.0, chunk_size=10):

    trim_ms = 0  # ms
    trim_ms_reverse = 0
    while trim_ms < len(sound):
        if sound[trim_ms:trim_ms + chunk_size].dBFS > silence_threshold:
            break
        trim_ms += chunk_size

    while trim_ms_reverse < len(sound.reverse()):
        if sound.reverse()[trim_ms_reverse:trim_ms_reverse + chunk_size].dBFS > silence_threshold:
            break
        trim_ms_reverse += chunk_size

    current_time = 0 + trim_ms
    end_time = len(sound) - trim_ms_reverse

    print(current_time, end_time)

    start_silence_sec = current_time / 1000
    end_silence_sec = end_time / 1000

    print(f"Start silence: {start_silence_sec:.2f} seconds")
    print(f"End silence: {end_silence_sec:.2f} seconds")

    return current_time, end_time

    

        

def asr_run(audio_path, cache_file):
    ####
    surah_meta, first_ayah , last_ayah = basic_data_check(surah_number)

    chunk_size = 2000  # Start with 1s chunks (adjustable)
    overlap = 500      # 500ms overlap between chunks
    min_chunk = 1000    # Minimum chunk size

    try:
        audio = AudioSegment.from_file(audio_path)
    except Exception as e:
        print("Invalid Audio file or audio file not supported. Check Error logs for more information")
        print("Error: ", e)
        print("Exiting Program... ")
        exit()    

    verses_data = [
        ayah for ayah in surah_meta['data']['ayahs']
        if first_ayah <= ayah['numberInSurah'] <= last_ayah
    ]

    # Remove Bismillah from first verse if needed
    if verses_data[0]['text'].startswith(bismillah_text):
        verses_data[0]['text'] = verses_data[0]['text'].replace(bismillah_text, "").strip()
        print("Bismillah text detect")

    # print("Verses Data: ", verses_data)

    print("Detecting silence in the audio ")
    
    silence_thresh = audio.dBFS - 16
    start_time, finish_time = detect_silence(audio, silence_thresh)

    total_duration = finish_time

    log_verses = []

    # Initialize cache
    try:
        with open(cache_file, "r") as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        cache = {
            "current_pos": start_time,  # in milliseconds
            "verses": [],
            "partial_transcript": ""
        }

    remaining_verses = [v for v in verses_data if not any(v['numberInSurah'] == found['verse_number'] for found in cache["verses"])]
    
    current_pos = cache["current_pos"]
    current_verse = remaining_verses[0] if remaining_verses else None
    next_verse = remaining_verses[1] if remaining_verses else None
    sim1_old = 0
    sim2_old = 0
    similarity_check = False

    while current_pos < total_duration and current_verse:
        chunk_size = max(min_chunk, chunk_size)
        end_pos = min(current_pos + chunk_size, total_duration)

        # Extract and transcribe chunk
        chunk = audio[current_pos:end_pos]
        chunk.export("temp_chunk.wav", format="wav")
        transcription = asr_model("temp_chunk.wav", generate_kwargs={"max_length": 400})["text"]

        # Update partial transcript
        cache["partial_transcript"] += " " + transcription
        print(f"Processing {current_pos/1000:.1f}s-{end_pos/1000:.1f}s: {get_display(arabic_reshaper.reshape(preprocess_text(transcription)))}")

        transcription = preprocess_text(transcription)
        preprocessed_current_verse =  preprocess_text(current_verse['text'])
       
        # current_verse['text'] = preprocess_text(current_verse['text'])
        if next_verse:
            preprocessed_next_verse = preprocess_text(next_verse['text'])
            # next_verse['text'] = preprocess_text(next_verse['text'])

        print("Current Verse: ", get_display(arabic_reshaper.reshape(preprocessed_current_verse)))
        if next_verse:
                token_similarity_next, seq_similarity_next = similarity_calculator(transcription, preprocessed_next_verse)
                print(f"Next verse: {get_display(arabic_reshaper.reshape(preprocessed_next_verse))}, with similarity: {token_similarity_next}% and {seq_similarity_next:.2f} ", )

        token_similarity_new, seq_similarity_new  = similarity_calculator(transcription, preprocessed_current_verse)

        print(f"Token Similarity Ratio: {token_similarity_new}%")
        print(f"SequenceMatcher Similarity Ratio: {seq_similarity_new:.2f}")

        # log_transcription(current_pos, end_pos,preprocess_text(transcription),preprocess_text(current_verse['text']), log_file)

        log_verses.append({
            "index": len(log_verses),
            "start_pos": current_pos,
            "end_pos": end_pos,
            "transcription": preprocess_text(transcription),
            "current_verse": preprocess_text(current_verse['text']),
            "token_similarity": token_similarity_new,
            "sequence_similarity": seq_similarity_new,
            "token_similarity_with_the_next_verse": token_similarity_next if token_similarity_next is not None else None,
            "seq_similarity_with_the_next_verse": seq_similarity_next if seq_similarity_next is not None else None
})


        matched = False

        # --- 🟩 1. Handle Bismillah as verse 0.1 ---

        bismillah_clean = preprocess_text(bismillah_text)

        if (current_verse['numberInSurah'] == 1 and 
            is_similar(transcription, bismillah_clean, 70, 0.7)):

            print("📿 Bismillah detected, saving as verse 0.1")
            cache["verses"].append({
                'verse_number': "0.1",
                'start_time': f"{int(current_pos//60000)}:{(current_pos//1000)%60:02}",
                'end_time': f"{int(end_pos//60000)}:{(end_pos//1000)%60:02}",
                'text_arabic': bismillah_text
            })
            current_pos = end_pos
            cache["current_pos"] = current_pos
            cache["partial_transcript"] = ""
            chunk_size = 1000
            matched = True
            continue  # Continue to next iteration

        

        if current_verse:
            if min_treshold(transcription, preprocessed_current_verse):
                print("Minimum Threshold requirements have been met")
                similarity_check = True

        # --- 🟨 2. Overlap with previous verse ---
        if cache["verses"]:
            last = cache["verses"][-1]
            last_text_clean = preprocess_text(last['text_arabic'])
            print("Last text clean", (get_display(arabic_reshaper.reshape(last_text_clean))))

            if is_similar(transcription, last_text_clean, 70, 0.65) and similarity_check == False:
                
                print(f"🔁 Overlap with verse {last['verse_number']}, extending end time")
                last['end_time'] = f"{int(end_pos//60000)}:{(end_pos//1000)%60:02}"
                current_pos = end_pos
                cache["current_pos"] = current_pos
                cache["partial_transcript"] = ""
                chunk_size = 1000
                matched = True
                continue  # Continue with same current_verse

        if similarity_check == True:
            sim1_new, sim2_new  = similarity_calculator(transcription, preprocessed_current_verse)

            print(f"Old Token: {sim1_old}, Old Sequence: {sim2_old}")

            if sim1_new >= sim1_old and sim2_new >= sim2_old:
                sim1_old = sim1_new
                sim2_old = sim2_new
            else:
                print("Noticed a drop in percentage. Matching.")
                print(f"✅ MATCHED Verse {current_verse['numberInSurah']}")
                print(f"endpos: {end_pos}")
                end_pos = end_pos - 1000

                cache["verses"].append({
                    'verse_number': str(current_verse['numberInSurah']),
                    'start_time': f"{int(current_pos//60000)}:{(current_pos//1000)%60:02}",
                    'end_time': f"{int(end_pos//60000)}:{(end_pos//1000)%60:02}",
                    'text_arabic': current_verse['text']
                })

                current_pos = end_pos
                cache["current_pos"] = current_pos
                cache["partial_transcript"] = ""
                remaining_verses.pop(0)
                current_verse = remaining_verses[0] if len(remaining_verses) >= 1 else None
                next_verse = remaining_verses[1] if len(remaining_verses) >= 2 else None
                chunk_size = 1000
                matched = True
        

        elif next_verse:
            if is_similar(transcription, preprocessed_next_verse, 70, 0.6):
                previous_verse_timings = find_best_match(log_verses, current_pos)
                previous_verse_end_time = previous_verse_timings['end_pos']

                cache["verses"].append({
                    'verse_number': str(current_verse['numberInSurah']),
                    'start_time': f"{int(current_pos//60000)}:{(current_pos//1000)%60:02}",
                    'end_time': f"{int(previous_verse_end_time//60000)}:{(previous_verse_end_time//1000)%60:02}",
                    'text_arabic': current_verse['text']
                })

                cache["verses"].append({
                    'verse_number': str(next_verse['numberInSurah']),
                    'start_time': f"{int(previous_verse_end_time//60000)}:{(previous_verse_end_time//1000)%60:02}",
                    'end_time': f"{int(end_pos//60000)}:{(end_pos//1000)%60:02}",
                    'text_arabic': next_verse['text']
                })
                current_pos = end_pos
                cache["current_pos"] = current_pos
                cache["partial_transcript"] = ""
                remaining_verses.pop(0)
                remaining_verses.pop(0)
                current_verse = remaining_verses[0] if len(remaining_verses) >= 1 else None
                next_verse = remaining_verses[1] if len(remaining_verses) >= 2 else None
                # current_verse = remaining_verses[1] if len(remaining_verses) > 1 else None

                chunk_size = 1000
                print("✅ MATCHED Verse with the next verse")
                matched = True

        if chunk_size == 29500:
                cache["verses"].append({
                    'verse_number': str(current_verse['numberInSurah']),
                    'start_time': f"{int(current_pos//60000)}:{(current_pos//1000)%60:02}",
                    'end_time': f"{int(end_pos//60000)}:{(end_pos//1000)%60:02}",
                    'text_arabic': current_verse['text']
                })
                current_pos = end_pos
                cache["current_pos"] = current_pos
                cache["partial_transcript"] = ""
                remaining_verses.pop(0)
                current_verse = remaining_verses[0] if len(remaining_verses) >= 1 else None
                next_verse = remaining_verses[1] if len(remaining_verses) >= 2 else None
                chunk_size = 1000
                matched = True
                print("Reached maximum Chunk size")


        if end_pos >= total_duration:
                cache["verses"].append({
                    'verse_number': str(current_verse['numberInSurah']),
                    'start_time': f"{int(current_pos//60000)}:{(current_pos//1000)%60:02}",
                    'end_time': f"{int(end_pos//60000)}:{(end_pos//1000)%60:02}",
                    'text_arabic': current_verse['text']
                })
                current_pos = end_pos
                cache["current_pos"] = current_pos
                cache["partial_transcript"] = ""
                print("Reached End of File")
                return cache["verses"]
        
        




        if matched:
            sim1_old = 0
            sim2_old = 0
            similarity_check = False
        

        else:
            # No match yet – keep increasing chunk
            chunk_size += 500
            

        # Save progress
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f)

    return cache["verses"]



    
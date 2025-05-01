from transformers import pipeline

surah_number = 113
audio_path = ''
all_verses = False
start_ayah = 1
end_ayah = 5


#Video editing
bg_type =  "shorts" #shorts or full_video
bg_path = ""

#ASR
asr_model = pipeline("automatic-speech-recognition", model="tarteel-ai/whisper-base-ar-quran")
cache_file="transcription_cache.json"


#Email

admin_email = ""
recipient_email = [""]

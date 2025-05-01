import requests
from config import surah_number

def generate_surah_metadata():
    response = requests.get(f"https://api.alquran.cloud/v1/surah/{surah_number}")

    if response.status_code == 200:
        data = response.json()
    else:
        print("Failed to retrieve data.")
    return data

def generate_translations(verses):
    #translation gen logic here
    # Add another attribute to the 'verses' dictionary for translation of each verse (trans_text) via API
    for verse in verses:
        # surah_number = surah_input  # Assuming 'surah_number' is stored for each verse
        verse_number = verse['verse_number']
        trans_ln = "en.sahih"
        
        # Build the API URL based on the surah and verse number, and the chosen translation
        api_url = f"http://api.alquran.cloud/v1/ayah/{surah_number}:{verse_number}/editions/{trans_ln}"
        
        try:
            # Request translation data from the API
            response = requests.get(api_url)
            response_data = response.json()
            # print("Data from respose:", response_data)
            
            # Check for successful response and extract the translation text
            if response_data['code'] == 200 and response_data['status'] == "OK":
                verse_translation = response_data['data'][0]['text']
                verse['trans_text'] = verse_translation  # Add translation to the verse dictionary
            else:
                verse['trans_text'] = "In the name of Allāh, the Entirely Merciful, the Especially Merciful."

        except Exception as e:
            print(f"Error fetching translation for Surah {surah_number}, Verse {verse_number}: {e}")
            verse['trans_text'] = "Error fetching translation"

    print("Verses: ", verses)
    return verses
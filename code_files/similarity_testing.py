from difflib import SequenceMatcher
from fuzzywuzzy import fuzz


def min_treshold(text1, text2, primary_threshold=60, secondary_threshold=0.60):
    primary_similarity = fuzz.token_set_ratio(text1, text2)
    secondary_similarity = SequenceMatcher(None, text1, text2).ratio()
    if primary_similarity >= primary_threshold and secondary_similarity >= secondary_threshold:
        return True
    return False

def is_similar(text1, text2, primary_threshold, secondary_threshold):
    # Use token_set_ratio for primary matching tolerance
    primary_similarity = fuzz.token_set_ratio(text1, text2)
    
    # If primary similarity is above threshold, perform a secondary fine-tuned check
    if primary_similarity >= primary_threshold:
        secondary_similarity = SequenceMatcher(None, text1, text2).ratio()
        return secondary_similarity >= secondary_threshold
    return False

def similarity_calculator(text1, text2):
    token_similarity = fuzz.token_set_ratio(text1, text2)
    sequence_similarity = SequenceMatcher(None, text1, text2).ratio()

    return token_similarity, sequence_similarity


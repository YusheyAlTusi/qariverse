# Qariverse: Quran Verse Audio Segmentation & Video Generator

Qariverse is a Python-based application that processes recitations of the Quran, automatically segments the audio by verse using ASR (Automatic Speech Recognition), matches transcriptions to verses using fuzzy logic, and generates visually engaging video clips for each verse — complete with Arabic text, translation, and synchronized audio.

---

## 🌟 Features

- 🎧 **ASR-Based Verse Segmentation**  
  Automatically detect and separate Quranic verses from long recitation audio files.

- 🧠 **Fuzzy Matching for Accuracy**  
  Matches transcribed text to Quranic verses using `Sequence` and `fuzzywuzzy`.

- 🖋️ **Arabic Text Rendering**  
  Properly reshapes Arabic script and uses BiDi rendering to display it correctly in videos.

- 🎬 **Beautiful Video Generation**  
  Generates high-quality videos using MoviePy with verse text, translation overlays, and background visuals.

- 📧 **Email Notifications**  
  Sends success/failure notifications upon video generation (configurable).

---

## 🧰 Requirements

Install the required Python packages using:

```bash
pip install -r requirements.txt


Note: This is the Beta version of my personal project. Looking forward for further improvizations. 

from api_calls import generate_translations
from config import surah_number as sno
from helpers import wrap_text ,time_to_seconds

from moviepy.editor import TextClip, CompositeVideoClip, ColorClip, AudioFileClip, VideoFileClip  # Add ColorClip here
from moviepy.config import change_settings
import os

change_settings({"IMAGEMAGICK_BINARY": "ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})

def create_video(audio_path, bg_type, bg_video_path, verses):
    

    for verse in verses:
        verse['start_time'] = time_to_seconds(verse['start_time'])
        verse['end_time'] = time_to_seconds(verse['end_time'])

    audio_vid = AudioFileClip(f"{audio_path}")
    audio_duration = audio_vid.duration  # Always use actual duration

    # Calculate total video duration

    background_duration = max(verses[-1]['end_time'], audio_duration)


    # Create the background with the calculated duration

    

    if bg_type == "shorts":

        background = (VideoFileClip(bg_video_path, audio=False)
                    .loop(duration=background_duration)
                    #.resize((1280, 720))
                    .set_duration(background_duration))

        
        # Create text clips for each verse with Arabic text and translation
        text_clips = []
        max_chars_per_line_ar = 50
        max_chars_per_line_en = 24
        for verse in verses:
            arabic_lines = wrap_text(verse['text_arabic'], max_chars_per_line_ar)
            translation_lines = wrap_text(verse['trans_text'], max_chars_per_line_en)

            y_position = 500
            for line in arabic_lines:
                line_clip = (TextClip(line, fontsize=140, color='yellow', font="Arial")
                            .set_position(("center", y_position))
                            .set_start(verse['start_time'])
                            .set_duration(verse['end_time'] - verse['start_time']))
                text_clips.append(line_clip)
                y_position += 160  # Adjust spacing between lines

            y_position = 800
            for line in translation_lines:
                line_clip = (TextClip(line, fontsize=110, color='white', font="fonts/BebasNeue-Regular.ttf")
                            .set_position(("center", y_position))
                            .set_start(verse['start_time'])
                            .set_duration(verse['end_time'] - verse['start_time']))
                text_clips.append(line_clip)
                y_position += 100  # Adjust spacing between lines

        # Bottom-right credit texts
        credit_text = f"Surah Falaq"  # Example: 71: Nuh
        credit_clip = (
            TextClip(
                credit_text,
                fontsize=50,
                font="fonts/BebasNeue-Regular.ttf",
                color='yellow',
                method='label'
            )
            .set_position(("right", "bottom"))
            .margin(right=10, bottom=80, opacity=0)
            .set_duration(background_duration)
        )

        # credit_w, credit_h = credit_clip.size

        transl_credit = (
            TextClip(
                "Translation by Saheeh International",
                fontsize=40,
                font="fonts/BebasNeue-Regular.ttf",
                color='white',
                method='label'
            )
            # .set_position((1200, "bottom"), relative=False) 
            .set_position(("right", "bottom"))
            .margin(right=10, bottom=20, opacity=0)
            .set_duration(background_duration)
        )

        # transl_w, transl_h = transl_clip.size

        text_clips.extend([credit_clip, transl_credit])

    elif bg_type == "full_screen":

        
        background = (VideoFileClip(bg_video_path, audio=False)
                    .loop(duration=background_duration)
                    .resize((1280, 720))
                    .set_duration(background_duration))
        
        
        # Create text clips for each verse with Arabic text and translation
        text_clips = []
        for verse in verses:
            arabic_text = (TextClip(verse['text_arabic'], fontsize=48, color='yellow', font="Arial")
                        .set_position(("center", 200))
                        .set_start(verse['start_time'])
                        .set_duration(verse['end_time'] - verse['start_time']))

            translation_text = (TextClip(verse['trans_text'], fontsize=38, color='white', font="fonts/BebasNeue-Regular.ttf")
                                .set_position(("center", 300))
                                .set_start(verse['start_time'])
                                .set_duration(verse['end_time'] - verse['start_time']))

            text_clips.append(arabic_text)
            text_clips.append(translation_text)

        # Bottom-right credit texts
        credit_text = f"Surah Falaq"  # Example: 71: Nuh
        credit_clip = (
            TextClip(
                credit_text,
                fontsize=30,
                font="fonts/BebasNeue-Regular.ttf",
                color='yellow',
                method='label'
            )
            .set_position(("right", "bottom"))
            .margin(right=10, bottom=50, opacity=0)
            .set_duration(background_duration)
        )

        # credit_w, credit_h = credit_clip.size

        transl_credit = (
            TextClip(
                "Translation by Saheeh International",
                fontsize=20,
                font="fonts/BebasNeue-Regular.ttf",
                color='white',
                method='label'
            )
            # .set_position((1200, "bottom"), relative=False) 
            .set_position(("right", "bottom"))
            .margin(right=10, bottom=20, opacity=0)
            .set_duration(background_duration)
        )

        # transl_w, transl_h = transl_clip.size

        text_clips.extend([credit_clip, transl_credit])

    else:
        raise ValueError(f"Unknown bg_type: {bg_type}")
    



    # Save frame at 2 seconds as an image
    



    # Combine background, text clips, and audio
    final_video = CompositeVideoClip([background, *text_clips]).set_audio(audio_vid)

    # frame = final_video.get_frame(30.0)  # Time in seconds
    # from PIL import Image
    # import numpy as np

    # img = Image.fromarray(np.uint8(frame))
    # img.save("frame_at_30_seconds.png")
    # print("Saved frame image at 2 seconds.")
    
    # Write the video to a file
    final_video_path = os.path.join("output", f"recitation_video_{sno}.mp4")
    final_video.write_videofile(final_video_path, fps=24)

    print("Video Generated succesfully")
    final_video.close() # or any other video object

    
    return final_video_path

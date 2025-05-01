from config import admin_email, audio_path, bg_type , bg_path, cache_file, recipient_email
import asyncio
from email_utils import send_email
import email_templates
from audio_asr import asr_run
from api_calls import generate_translations
import os
from video_editing import create_video
import time
import traceback

if __name__ == "__main__":
    try:
        if os.path.exists(cache_file):
            os.remove(cache_file)
        start_time = time.time()
        verses_dict = asr_run(audio_path, cache_file)
        generate_translations(verses_dict)
        print("Verses: ", verses_dict)
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time
        formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        print(f"Time taken to complete the operation: {formatted_time}")

        create_video(audio_path, bg_type, bg_path,  verses_dict)
        print("Succesfully completed")

        subject_user, body_user = email_templates.get_success_user_email( formatted_time)
        asyncio.run(send_email(recipient_email[0], subject_user, body_user))


        subject_admin, body_admin = email_templates.get_success_admin_email(recipient_email, formatted_time)
        asyncio.run(send_email(admin_email, subject_admin, body_admin))


    except Exception as e:
        tb_str = traceback.format_exc()
        print("Failed to complete the process:", e)
        print("Traceback: ", tb_str)

        subject_user, body_user = email_templates.get_failure_user_email()
        asyncio.run(send_email(recipient_email[0], subject_user, body_user))

        subject_admin, body_admin = email_templates.get_failure_admin_email(recipient_email, e)
        asyncio.run(send_email(admin_email, subject_admin, body_admin))




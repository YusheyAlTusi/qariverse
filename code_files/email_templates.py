# email_templates.py

def get_success_user_email(time_taken):
    return (
        "🎉 Your Quran Video is Ready!",
        f"""
Assalamu Alaikum,

Your Quran recitation video has been successfully generated! 🙌

📜 
⏱ Time Taken: {time_taken}

You can now view, download, or edit your video.

JazakAllah Khair,  
The Qariverse Team
"""
    )

def get_success_admin_email(recipient_email, time_taken):
    return (
        f"✅ Video Generated for {recipient_email}",
        f"""
User {recipient_email} has successfully generated a Quran video.

📜 
🕒 Duration: {time_taken}
"""
    )

def get_failure_user_email():
    return (
        "⚠️ Video Generation Failed",
        """
Assalamu Alaikum,

We regret to inform you that your Quran recitation video could not be generated due to an unexpected error.

Our technical team has been notified and will look into it shortly.

Please try again later.

JazakAllah Khair,  
The Qariverse Team
"""
    )

def get_failure_admin_email(recipient_email, error):
    return (
        f"❌ ERROR: Video Generation Failed for {recipient_email}",
        f"""
🚨 URGENT ERROR 🚨

A video generation attempt by {recipient_email} has FAILED.

❌ Exception:
{str(error)}

Please investigate immediately.
"""
    )

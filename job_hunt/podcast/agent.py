# podcast/ai.py
import os
import tempfile
import pyttsx3
from groq import Groq
from django.conf import settings

GROQ_API_KEY = os.getenv("GROQ_API_KEY", getattr(settings, "GROQ_API_KEY", None))
client = Groq(api_key=GROQ_API_KEY)

def generate_podcast_script(topic: str, user_interest: str) -> str:
    system_msg = {
        "role": "system",
        "content": (
            "You are a professional podcast script writer. Write a spoken podcast script with:\n"
            "- Hook\n- Short story/example\n- 3 practical insights\n- Closing call-to-action\n"
            "Tone: conversational, simple English. Length: ~2-4 minutes."
        )
    }
    user_msg = {"role": "user", "content": f"Topic: {topic}\nUser interest: {user_interest}\nReturn the final script only."}
    try:
        response = client.chat.completions.create(
            messages=[system_msg, user_msg],
            model="llama3-70b-8192",
            max_tokens=900,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Groq Error:", e)
        return None

def generate_audio_from_script(script: str) -> str:
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 165)
        engine.setProperty('volume', 0.9)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        path = tmp.name
        engine.save_to_file(script, path)
        engine.runAndWait()
        return path
    except Exception as e:
        print("TTS Error:", e)
        return None

def get_thumbnail_url(topic: str) -> str:
    safe = topic.replace(" ", "+")
    return f"https://source.unsplash.com/featured/?{safe}"

import os
import io
import time
import uuid
import requests

from groq import Groq
from django.conf import settings
from deepgram import DeepgramClient

from dotenv import load_dotenv
from .cloudinary import upload_audio_to_cloudinary

load_dotenv()
# ==============================
# Clients
# ==============================

dg_client = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))


GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY")


client = Groq(api_key="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")


# ==============================
# Script Generation (Groq LLM)
# ==============================

def generate_podcast_script(topic: str, user_interest: str) -> str:
    system_msg = {
        "role": "system",
        "content": (
            "You are a professional podcast script writer. Write a spoken podcast script with:\n"
            "- Hook\n- Short story/example\n- 3 practical insights\n- Closing call-to-action\n"
            "Tone: conversational, simple English. Length: max 400 characters.\n"
        ),
    }

    user_msg = {
        "role": "user",
        "content": (
            f"Topic: {topic}\n"
            f"User interest: {user_interest}\n"
            "Return the final script only."
        ),
    }

    try:
        response = client.chat.completions.create(
            messages=[system_msg, user_msg],
            model="openai/gpt-oss-120B",
            max_tokens=300,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Groq Error:", e)
        return None


# ==============================
# Helpers
# ==============================

def generate_unique_filename(extension="mp3"):
    return f"{uuid.uuid4()}.{extension}"


def chunk_text(text: str, max_chars: int = 800):
    sentences = text.replace("\n", " ").split(". ")
    chunks = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current) + len(sentence) <= max_chars:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "

    if current.strip():
        chunks.append(current.strip())

    return chunks


def split_text_for_tts(text: str, max_tokens: int = 1000) -> list:
    """
    Split text into chunks based on token estimation.
    Deepgram handles long text well, so this is only for safety.
    """
    words = text.split()
    chunks = []

    current_chunk = []
    current_count = 0

    for word in words:
        word_tokens = 1.3  # rough estimate

        if current_count + word_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_count = word_tokens
        else:
            current_chunk.append(word)
            current_count += word_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# ==============================
# Deepgram TTS + Upload
# ==============================

def text_to_speech_and_upload(text: str, voice: str = "aura-asteria-en") -> list:
    """
    Convert text → Deepgram TTS → upload to Cloudinary
    Uses streaming bytes (no temp files).
    """

    # Deepgram supports long text, chunk only when large
    text_chunks = [text] if len(text) < 4000 else split_text_for_tts(text)

    audio_urls = []

    for i, chunk in enumerate(text_chunks):
        try:
            response = dg_client.speak.rest(
                {"text": chunk},           # payload
                {
                    "model": voice,
                    "encoding": "mp3",
                },
            )

            audio_buffer = io.BytesIO(response.stream)
            audio_buffer.seek(0)

            audio_url = upload_audio_to_cloudinary(
                audio_bytes=audio_buffer.getvalue(),
                public_id_prefix=f"dg_tts_segment_{i+1}",
            )

            print(f"Deepgram audio uploaded: {audio_url}")
            audio_urls.append(audio_url)

        except Exception as e:
            print(f"Deepgram Error on chunk {i+1}: {str(e)}")
            continue

    return audio_urls


# ==============================
# Main Processing
# ==============================

def process_podcast_text(text: str, voice: str = "aura-asteria-en") -> dict:
    """
    Convert full podcast text into audio segments.
    """

    audio_urls = text_to_speech_and_upload(text, voice)

    return {
        "audio_segments": audio_urls,
        "total_segments": len(audio_urls),
        "voice": voice,
        "timestamp": time.time(),
    }


# ==============================
# Thumbnail
# ==============================

def get_thumbnail_url(topic: str) -> str:
    """
    Unsplash removed dynamic featured endpoint.
    Replace with your own service if needed.
    """
    return "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=800&q=80"

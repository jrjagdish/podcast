import io
import os
from groq import Groq
from django.conf import settings
import requests
import uuid
from .cloudinary import upload_audio_to_cloudinary
import time

GROQ_API_KEY = os.getenv("GROQ_API_KEY", getattr(settings, "GROQ_API_KEY", None))
client = Groq(api_key=GROQ_API_KEY)


def generate_podcast_script(topic: str, user_interest: str) -> str:
    system_msg = {
        "role": "system",
        "content": (
            "You are a professional podcast script writer. Write a spoken podcast script with:\n"
            "- Hook\n- Short story/example\n- 3 practical insights\n- Closing call-to-action\n"
            "Tone: conversational, simple English. Length: Length: max 400 characters.\n"
        ),
    }
    user_msg = {
        "role": "user",
        "content": f"Topic: {topic}\nUser interest: {user_interest}\nReturn the final script only.",
    }
    try:
        response = client.chat.completions.create(
            messages=[system_msg, user_msg],
            model="openai/gpt-oss-20B",
            max_tokens=900,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print("Groq Error:", e)
        return None


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
    """Split text into chunks of approximately max_tokens."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_count = 0

    for word in words:
        # Each word is approximately 1-1.5 tokens, use 1.3 for safety
        word_tokens = 1.3

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


def text_to_speech_and_upload(text: str, voice: str = "Aaliyah-PlayAI") -> list:
    text_chunks = split_text_for_tts(text)
    audio_urls = []

    for i, chunk in enumerate(text_chunks):
        try:
            response = client.audio.speech.create(
                model="playai-tts", voice=voice, response_format="wav", input=chunk
            )

            # ✅ FIX IS HERE
            audio_buffer = io.BytesIO()
            response.write_to_file(audio_buffer)
            audio_buffer.seek(0)

            audio_url = upload_audio_to_cloudinary(
                audio_bytes=audio_buffer.getvalue(),  # 🔥 THIS LINE
                public_id_prefix=f"tts_segment_{i+1}",
            )
            print("audio updated"+audio_url)

            audio_urls.append(audio_url)

            if i < len(text_chunks) - 1:
                time.sleep(6)

        except Exception as e:
            print(f"Error processing chunk {i+1}: {str(e)}")
            raise

    return audio_urls


def process_podcast_text(text: str, voice: str = "Aaliyah-PlayAI") -> dict:
    """
    Main function to process podcast text into audio segments.

    Args:
        text: Text content for the podcast
        voice: Voice to use for TTS

    Returns:
        Dictionary with audio URLs and metadata
    """
    audio_urls = text_to_speech_and_upload(text, voice)

    return {
        "audio_segments": audio_urls,
        "total_segments": len(audio_urls),
        "voice": voice,
        "timestamp": time.time(),
    }


def get_thumbnail_url(topic: str) -> str:
    safe = topic.replace(" ", "+")
    return f"https://source.unsplash.com/featured/?{safe}"

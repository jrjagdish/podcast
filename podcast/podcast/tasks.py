# podcast/tasks.py
import os
from celery import shared_task
from django.utils import timezone

from .cloudinary import upload_audio_to_cloudinary
from .models import PodcastEpisode
from .agent import generate_podcast_script,text_to_speech_and_upload, process_podcast_text, get_thumbnail_url
from .uploaders import upload_to_supabase
from .utils import estimate_tokens_for_script

@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def process_podcast_episode(self, episode_id, user_interest=None, tone="motivational", length="short"):
    try:
        episode = PodcastEpisode.objects.get(id=episode_id)
        episode.status = "generating"
        episode.save()

        script = generate_podcast_script(topic = episode.title, user_interest = user_interest or episode.title)

        audio_urls = text_to_speech_and_upload(script)

        audio_url = audio_urls[0] if audio_urls else None

        thumbnail_url = get_thumbnail_url(topic=episode.title)
        # 5) Save update
        episode.audio_url = audio_url
        episode.image_url = thumbnail_url
        episode.status = "completed"
        episode.tokens_used = estimate_tokens_for_script(script)
        episode.save()

        return {"audio_url": audio_url}

    except Exception as exc:
        try:
            episode = PodcastEpisode.objects.get(id=episode_id)
            episode.status = "failed"
            episode.save()
        except Exception:
            pass
        raise self.retry(exc=exc)

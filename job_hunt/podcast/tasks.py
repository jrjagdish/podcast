# podcast/tasks.py
import os
from celery import shared_task
from django.utils import timezone
from .models import PodcastEpisode
from .agent import generate_podcast_script, generate_audio_from_script, get_thumbnail_url
from .uploaders import upload_to_supabase
from .utils import estimate_tokens_for_script

@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def process_podcast_episode(self, episode_id, user_interest=None, tone="motivational", length="short"):
    try:
        episode = PodcastEpisode.objects.get(id=episode_id)
        episode.status = "generating"
        episode.save()

        # 1) Generate script
        script = generate_podcast_script(topic=episode.title, user_interest=user_interest or episode.title)
        if not script:
            episode.status = "failed"
            episode.save()
            return {"error": "script_failed"}

        episode.script = script
        episode.save()

        # 2) Generate audio (TTS)
        audio_path = generate_audio_from_script(script)
        if not audio_path:
            episode.status = "failed"
            episode.save()
            return {"error": "tts_failed"}

        # 3) Upload to Supabase
        audio_url = upload_to_supabase(audio_path)
        try:
            os.remove(audio_path)
        except Exception:
            pass

        # 4) Thumbnail
        image_url = get_thumbnail_url(episode.title)

        # 5) Save update
        episode.audio_url = audio_url
        episode.image_url = image_url
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

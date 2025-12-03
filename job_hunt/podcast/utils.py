# utils.py
from django.utils import timezone
from .models import PodcastEpisode

FREE_DAILY_LIMIT = 1  

# podcast/utils.py
from django.utils import timezone
from .models import PodcastEpisode

FREE_DAILY_LIMIT = 1

def can_generate_episode(user):
    plan = getattr(getattr(user, "subscription", None), "plan", "free")
    if plan in ("pro", "enterprise"):
        return True, ""
    today = timezone.now().date()
    cnt = PodcastEpisode.objects.filter(user=user, created_at__date=today).count()
    if cnt >= FREE_DAILY_LIMIT:
        return False, "Daily free episode limit reached. Upgrade to Pro."
    return True, ""

def estimate_tokens_for_script(script_text):
    return max(1, len(script_text) // 4)

def get_thumbnail_url(title):
    title = title.lower()

    if "motivation" in title or "focus" in title:
        return "https://source.unsplash.com/featured/?motivation"

    if "calm" in title or "sleep" in title:
        return "https://source.unsplash.com/featured/?calm"

    if "learn" in title or "tech" in title or "coding" in title:
        return "https://source.unsplash.com/featured/?technology"

    return "https://source.unsplash.com/featured/?podcast"


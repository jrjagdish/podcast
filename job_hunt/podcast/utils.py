# utils.py
from django.utils import timezone
from .models import PodcastEpisode

FREE_DAILY_LIMIT = 1  

def can_generate_episode(user):
    """
    Return (True, '') if the user can request a new episode now.
    Otherwise return (False, message).
    """
   
    plan = getattr(getattr(user, "subscription", None), "plan", "free")

    if plan == "pro" or plan == "enterprise":
        return True, ""

    
    today = timezone.now().date()
    episodes_today = PodcastEpisode.objects.filter(user=user, created_at__date=today).count()
    if episodes_today >= FREE_DAILY_LIMIT:
        return False, "Daily free episode limit reached. Upgrade to Pro for unlimited episodes."
    return True, ""

# models.py
import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

# ---------- Optional small lookup for plan choices ----------
PLAN_CHOICES = [
    ("free", "Free"),
    ("pro", "Pro"),
    ("enterprise", "Enterprise"),
]

# ---------- UserSubscription (keeps user model untouched) ----------
class UserSubscription(models.Model):
    """
    Keeps subscription/plan info separate (safer if you already have a User table).
    Attach one-to-one to the user so checking plan is easy.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription")
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default="free")
    # You can add payment metadata here later (stripe_customer_id, renewal_at, etc.)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} ({self.plan})"


# ---------- UserPreferences ----------
class UserPreferences(models.Model):
    """
    Stores the user's podcast preferences (interests, tone, length).
    Keep small and JSON-backed for flexibility.
    """
    TONE_CHOICES = [
        ("motivational", "Motivational"),
        ("calm", "Calm"),
        ("informative", "Informative"),
    ]
    LENGTH_CHOICES = [
        ("short", "Short"),    # ~2-4 mins
        ("medium", "Medium"),  # ~5-8 mins
        ("long", "Long"),      # 9+ mins
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="preferences")
    interests = models.JSONField(default=list)  # e.g. ["productivity","coding"]
    tone = models.CharField(max_length=50, choices=TONE_CHOICES, default="motivational")
    episode_length = models.CharField(max_length=20, choices=LENGTH_CHOICES, default="short")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"


# ---------- PodcastEpisode ----------
class PodcastEpisode(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("generating", "Generating"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    EPISODE_TYPE = [
        ("free", "Free"),
        ("premium", "Premium"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="episodes")

    title = models.CharField(max_length=255)
    script = models.TextField(null=True, blank=True)

    audio_url = models.URLField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)  

    duration = models.IntegerField(null=True, blank=True)  # seconds
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    episode_type = models.CharField(max_length=10, choices=EPISODE_TYPE, default="free")

    # Cost-tracking (helpful for throttling free users)
    tokens_used = models.IntegerField(default=0)  
    is_limited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.user.email})"

    @property
    def is_playable(self):
        return self.status == "completed" and bool(self.audio_url)

# podcast/serializers.py
from rest_framework import serializers
from .models import PodcastEpisode

class PodcastEpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PodcastEpisode
        fields = "__all__"
        read_only_fields = ["id","script","audio_url","image_url","duration","status","created_at","tokens_used"]

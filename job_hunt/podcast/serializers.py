from rest_framework import serializers
from .models import PodcastEpisode

class PodcastEpisodeSerializer(serializers.ModelSerializer):
    class meta:
        model = PodcastEpisode
        fields = "__all__"
        read_only_fields = ("id", "script", "status", "image_url")
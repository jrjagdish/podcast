from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import PodcastEpisode
from .serializers import PodcastEpisodeSerializer
from .utils import get_thumbnail_url


# Create your views here.
class PodcastEpisodeViewSet(viewsets.ModelViewSet):
    queryset = PodcastEpisode.objects.all()
    serializer_class = PodcastEpisodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PodcastEpisode.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        title = request.data.get("title")
        audio_url = request.data.get("audio_url")

        if not title:
            return Response({"error": "title is required"}, status=400)
        if not audio_url:
            return Response({"error": "audio_url is required"}, status=400)
        thumbnail = get_thumbnail_url(title)

        episode = PodcastEpisode.objects.create(
            user=request.user,
            title=title,
            status="pending",
            audio_url=audio_url,
            image_url=thumbnail,
        )
        serializer = self.get_serializer(episode)
        return Response(serializer.data, status=201)

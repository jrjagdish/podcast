from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import PodcastEpisode
from .serializers import PodcastEpisodeSerializer
from .tasks import process_podcast_episode
from .utils import can_generate_episode

class PodcastEpisodeViewSet(viewsets.ModelViewSet):
    serializer_class = PodcastEpisodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PodcastEpisode.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        title = request.data.get("title")
        interest = request.data.get("interest", title)

        if not title:
            return Response({"error": "title is required"}, status=status.HTTP_400_BAD_REQUEST)

        allowed, msg = can_generate_episode(request.user)
        if not allowed:
            return Response({"error": msg}, status=status.HTTP_403_FORBIDDEN)

        episode = PodcastEpisode.objects.create(
            user=request.user,
            title=title,
            status="pending",
            episode_type=getattr(request.user, "subscription", None).plan if getattr(request.user, "subscription", None) else "free",
            is_limited=(getattr(request.user, "subscription", None).plan == "free") if getattr(request.user, "subscription", None) else True,
        )

        # enqueue background task
        process_podcast_episode.delay(str(episode.id), user_interest=interest)

        serializer = self.get_serializer(episode)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

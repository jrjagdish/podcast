from rest_framework.routers import DefaultRouter
from .views import PodcastEpisodeViewSet
from django.urls import path

router = DefaultRouter()
router.register("episodes", PodcastEpisodeViewSet, basename="episodes")

urlpatterns = router.urls

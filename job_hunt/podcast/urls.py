from rest_framework.routers import DefaultRouter
from .views import PodcastEpisodeViewSet

router = DefaultRouter()
router.register("episodes", PodcastEpisodeViewSet, basename="episodes")

urlpatterns = router.urls

from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import BookViewSet, ReadingGoalView, StatsView

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="book")

urlpatterns = router.urls + [
    path('goal/', ReadingGoalView.as_view()),
    path('stats/', StatsView.as_view()),
]
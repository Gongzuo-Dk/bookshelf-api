from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book, ReadingGoal
from .serializers import BookSerializer, ReadingGoalSerializer, StatsSerializer
import datetime


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "genre"]
    search_fields = ["title", "author"]
    ordering_fields = ["rating", "created_at", "finish_date"]

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReadingGoalView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        year = request.query_params.get("year", datetime.date.today().year)
        try:
            goal = ReadingGoal.objects.get(user=request.user, year=year)
            serializer = ReadingGoalSerializer(goal)
            return Response(serializer.data)
        except ReadingGoal.DoesNotExist:
            return Response(
                {"detail": "No goal set for this year."},
                status=status.HTTP_404_NOT_FOUND
            )
        
    def post(self, request):
        serializer = ReadingGoalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        year = request.data.get("year", datetime.date.today().year)
        try:
            goal = ReadingGoal.objects.get(user=request.user, year=year)
        except ReadingGoal.DoesNotExist:
            return Response(
                {"detail": "No goal found for this year."},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ReadingGoalSerializer(goal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class StatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        current_year = datetime.date.today().year
        books = Book.objects.filter(user=user)

        total_books = books.count()
        completed_this_year = books.filter(
            status="completed",
            finish_date__year=current_year
        ).count()
        currently_reading = books.filter(status="reading").count()
        want_to_read = books.filter(status="want_to_read").count()
        abandoned = books.filter(status="abandoned").count()

        avg = books.filter(status="completed").aggregate(Avg("rating"))
        average_rating = round(avg["rating__avg"], 2) if avg["rating__avg"] else None

        favourite_genre = (
            books.values("genre").annotate(count=Count("genre")).order_by("-count").first()
        )
        favourite_genre = favourite_genre["genre"] if favourite_genre else None

        goal_progress = None
        try:
            goal = ReadingGoal.objects.get(user=user, year=current_year)
            if goal.target_books > 0:
                goal_progress = round((completed_this_year / goal.target_books) * 100, 1)
        except ReadingGoal.DoesNotExist:
            pass

        data = {
            "total_books": total_books,
            "completed_this_year": completed_this_year,
            "currently_reading": currently_reading,
            "want_to_read": want_to_read,
            "abandoned": abandoned,
            "average_rating": average_rating,
            "favourite_genre": favourite_genre,
            "goal_progress": goal_progress,
        }

        serializer = StatsSerializer(data)
        return Response(serializer.data)
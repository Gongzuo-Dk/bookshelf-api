from rest_framework import serializers
from .models import Book, ReadingGoal

class BookSerializer(serializers.ModelSerializer):

    reading_progress = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "genre",
            "description",
            "status",
            "rating",
            "review",
            "current_page",
            "total_pages",
            "reading_progress",
            "start_date",
            "finish_date",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_reading_progress(self, obj):
        if obj.total_pages:
            return round((obj.current_page / obj.total_pages) * 100, 1)
        return None
    
    def validate_rating(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    
    def validate(self, data):
        status = data.get("status", getattr(self.instance, "status", None))
        rating = data.get("rating", getattr(self.instance, "rating", None))

        if rating is not None and status != "completed":
            raise serializers.ValidationError(
                {"rating": "You can only rate a book you have completed."}
            )
        return data
    

class ReadingGoalSerializer(serializers.ModelSerializer):
    books_completed_this_year = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = ReadingGoal
        fields = [
            "id",
            "year",
            "target_books",
            "books_completed_this_year",
            "progress_percentage",
        ]
        read_only_fields = ["id"]

    def get_books_completed_this_year(self, obj):
        return Book.objects.filter(
            user=obj.user,
            status="completed",
            finish_date__year=obj.year
        ).count()
    
    def get_progress_percentage(self, obj):
        completed = self.get_books_completed_this_year(obj)
        if obj.target_books > 0:
            return round((completed / obj.target_books) * 100, 1)
        return 0
    
class StatsSerializer(serializers.Serializer):
    total_books = serializers.IntegerField()
    completed_this_year = serializers.IntegerField()
    currently_reading = serializers.IntegerField()
    want_to_read = serializers.IntegerField()
    abandoned = serializers.IntegerField()
    average_rating = serializers.FloatField(allow_null=True)
    favourite_genre = serializers.CharField(allow_null=True)
    goal_progress = serializers.FloatField(allow_null=True)
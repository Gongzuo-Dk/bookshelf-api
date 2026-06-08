from rest_framework import serializers
from .models import Book

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
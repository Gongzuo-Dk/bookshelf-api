from django.db import models
from django.conf import settings

class Book(models.Model):

    STATUS_CHOICES = [
        ("want_to_read", "Want to Read"),
        ("reading", "Reading"),
        ("completed", "Completed"),
        ("abandoned", "Abandoned"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="books"
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=150)
    genre = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="want_to_read"
    )
    rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(blank=True)
    current_page = models.IntegerField(default=0)
    total_pages = models.IntegerField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

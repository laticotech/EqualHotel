# reviews/models.py
from django.db import models


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )

    guest_name = models.CharField(max_length=100)
    guest_country = models.CharField(max_length=100, blank=True)
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    stay_date = models.DateField(blank=True, null=True)

    # Moderation
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.guest_name} - {self.rating} stars"
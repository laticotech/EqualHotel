# contact/models.py
from django.db import models


class ContactInquiry(models.Model):
    INQUIRY_TYPES = (
        ('general', 'General Inquiry'),
        ('booking', 'Booking Question'),
        ('group', 'Group Booking'),
        ('event', 'Event Inquiry'),
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Contact inquiries"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.name}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
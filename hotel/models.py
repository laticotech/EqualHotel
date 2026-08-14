# hotel/models.py
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.forms import ModelForm, TextInput, Textarea
from embed_video.fields import EmbedVideoField

from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)

    # Hotel policies
    check_in_time = models.TimeField(default='14:00')
    check_out_time = models.TimeField(default='12:00')
    cancellation_policy = models.TextField(blank=True)
    pet_policy = models.TextField(blank=True)

    # about company
    about = RichTextUploadingField(blank=True)
    about_video = EmbedVideoField(blank=True)

    # Social media
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)

    # Images
    logo = models.ImageField(upload_to='hotel/logo/', blank=True)
    featured_image = models.ImageField(upload_to='hotel/')

    # Settings
    is_accepting_bookings = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class HotelAmenity(models.Model):
    AMENITY_CATEGORIES = (
        ('general', 'General'),
        ('room', 'Room Amenities'),
        ('bathroom', 'Bathroom'),
        ('dining', 'Dining'),
        ('business', 'Business'),
        ('leisure', 'Leisure'),
        ('safety', 'Safety & Security'),
    )

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='amenities')
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)  # FontAwesome class
    category = models.CharField(max_length=20, choices=AMENITY_CATEGORIES)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Hotel amenities"
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='team_members')
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='team/', blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} - {self.position}"


class Event(models.Model):
    EVENT_TYPES = [
        ('conference', 'Conference'),
        ('wedding', 'Wedding'),
        ('party', 'Party'),
        ('meeting', 'Business Meeting'),
        ('seminar', 'Seminar'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='other')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    max_attendees = models.PositiveIntegerField(default=0)
    current_attendees = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the custom user model
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date']

    def __str__(self):
        return self.title

    @property
    def is_upcoming(self):
        return self.start_date > timezone.now()

    @property
    def available_spots(self):
        return self.max_attendees - self.current_attendees

    @property
    def is_full(self):
        return self.max_attendees > 0 and self.current_attendees >= self.max_attendees


class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
        ('no_show', 'No Show'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    special_requirements = models.TextField(blank=True)
    number_of_guests = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    registration_date = models.DateTimeField(auto_now_add=True)
    confirmation_sent = models.BooleanField(default=False)
    confirmation_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-registration_date']
        unique_together = ['event', 'email']  # Prevent duplicate registrations

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"

    def save(self, *args, **kwargs):
        # Update event attendee count when registration is confirmed
        if self.status == 'confirmed' and self.pk:
            old_status = EventRegistration.objects.get(pk=self.pk).status
            if old_status != 'confirmed':
                self.event.current_attendees += self.number_of_guests
                self.event.save()
        elif self.status != 'confirmed' and self.pk:
            old_status = EventRegistration.objects.get(pk=self.pk).status
            if old_status == 'confirmed':
                self.event.current_attendees -= self.number_of_guests
                self.event.save()
        super().save(*args, **kwargs)
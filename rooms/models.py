# rooms/models.py
from django.db import models


class RoomType(models.Model):
    hotel = models.ForeignKey('hotel.Hotel', on_delete=models.CASCADE, related_name='room_types')
    name = models.CharField(max_length=100)  # Deluxe, Suite, Standard
    slug = models.SlugField(unique=True)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(help_text="Maximum number of guests")
    size = models.CharField(max_length=50, blank=True)  # 35 sqm, 450 sqft
    bed_type = models.CharField(max_length=100, blank=True)  # King bed, Twin beds

    # Images
    featured_image = models.ImageField(upload_to='room_types/')

    # Settings
    is_available = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'base_price']

    def __str__(self):
        return self.name


class Room(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    floor = models.PositiveIntegerField(default=1)
    view_description = models.CharField(max_length=200, blank=True)  # Ocean view, Garden view
    special_features = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['floor', 'room_number']

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type.name}"


class RoomImage(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/')
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ['display_order']


class RoomAmenity(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='amenities')
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name
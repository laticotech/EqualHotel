# gallery/models.py
from django.db import models


class GalleryCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Gallery categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class GalleryImage(models.Model):
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='gallery/')
    title = models.CharField(max_length=200, blank=True)
    caption = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', '-uploaded_at']

    def __str__(self):
        return self.title if self.title else f"Image {self.id}"
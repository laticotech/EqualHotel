from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.html import mark_safe

class User(AbstractUser):
    email = models.EmailField(unique=True, null=False)
    username = models.CharField(max_length=100, unique=True)  # Added unique=True

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=300)
    bio = models.CharField(max_length=1000, null=True, blank=True)
    profile_pic = models.ImageField(blank=True, upload_to='images/user_profile/', default='user.png')
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def profile_image_tag(self):
        return mark_safe('<img src="%s" width="50" height="50"/>' % (self.profile_pic.url))
    profile_image_tag.short_description = "Profile Picture"

    class Meta:
        verbose_name_plural = "Profile"
from django.contrib import admin
from .models import Profile, User
from django.contrib.auth.admin import UserAdmin


# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone', 'address', 'profile_image_tag']

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)



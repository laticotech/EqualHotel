# gallery/admin.py
from django.contrib import admin
from .models import GalleryCategory, GalleryImage


@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_order', 'image_count']
    list_editable = ['display_order']
    search_fields = ['name']

    def image_count(self, obj):
        return obj.images.count()

    image_count.short_description = 'Images'


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'display_order', 'is_featured', 'uploaded_at']
    list_filter = ['category', 'is_featured', 'uploaded_at']
    list_editable = ['display_order', 'is_featured']
    search_fields = ['title', 'caption', 'category__name']
    readonly_fields = ['uploaded_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'title', 'caption')
        }),
        ('Image', {
            'fields': ('image', 'display_order', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        })
    )
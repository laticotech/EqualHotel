from django.contrib import admin
from django.utils.html import format_html
from .models import Hotel, HotelAmenity, TeamMember, Event, EventRegistration


# Inline admin classes
class HotelAmenityInline(admin.TabularInline):
    model = HotelAmenity
    extra = 1
    fields = ['name', 'category', 'icon', 'is_featured', 'description']
    ordering = ['category', 'name']


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    fields = ['name', 'position', 'photo_tag', 'email', 'phone', 'is_active', 'display_order']
    readonly_fields = ['photo_tag']
    ordering = ['display_order', 'name']

    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.photo.url)
        return "No Photo"
    photo_tag.short_description = 'Photo'


# Main admin classes
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'phone',
        'email',
        'is_accepting_bookings',
        'created_at',
        'logo_tag'
    ]
    list_filter = [
        'is_accepting_bookings',
        'created_at'
    ]
    search_fields = [
        'name',
        'address',
        'phone',
        'email'
    ]
    list_editable = ['is_accepting_bookings']
    readonly_fields = [
        'created_at',
        'updated_at',
        'logo_tag',
        'featured_image_tag',
        'about_video_preview'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'tagline',
                'description',
                'logo',
                'logo_tag',
                'featured_image',
                'featured_image_tag'
            )
        }),
        ('About Us Content', {
            'fields': (
                'about',
                'about_video',
                'about_video_preview'
            )
        }),
        ('Contact Information', {
            'fields': (
                'address',
                'phone',
                'email',
                'website'
            )
        }),
        ('Hotel Policies', {
            'fields': (
                'check_in_time',
                'check_out_time',
                'cancellation_policy',
                'pet_policy'
            )
        }),
        ('Social Media', {
            'classes': ('collapse',),
            'fields': (
                'facebook_url',
                'instagram_url',
                'twitter_url'
            )
        }),
        ('Settings', {
            'fields': (
                'is_accepting_bookings',
            )
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at'
            )
        }),
    )
    inlines = [HotelAmenityInline, TeamMemberInline]
    ordering = ['name']
    date_hierarchy = 'created_at'

    def logo_tag(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" />', obj.logo.url)
        return "No Logo"
    logo_tag.short_description = 'Logo'

    def featured_image_tag(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" width="100" height="75" />', obj.featured_image.url)
        return "No Featured Image"
    featured_image_tag.short_description = 'Featured Image'

    def about_video_preview(self, obj):
        if obj.about_video:
            # Extract video ID from YouTube URL for preview
            video_url = str(obj.about_video)
            if 'youtube.com' in video_url or 'youtu.be' in video_url:
                # Simple preview - show the URL and a clickable link
                return format_html(
                    '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #008080;">'
                    '<strong>Video URL:</strong><br>'
                    '<a href="{}" target="_blank" style="word-break: break-all;">{}</a><br><br>'
                    '<small style="color: #666;">This YouTube video will be embedded on the About Us page.</small>'
                    '</div>',
                    video_url, video_url
                )
            else:
                return format_html(
                    '<div style="background: #fff3cd; padding: 10px; border-radius: 4px; border: 1px solid #ffeaa7;">'
                    '<strong>Note:</strong> Please provide a valid YouTube URL'
                    '</div>'
                )
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; color: #666;">'
            '<i class="fas fa-video" style="font-size: 24px; margin-bottom: 10px;"></i><br>'
            'No video URL provided'
            '</div>'
        )
    about_video_preview.short_description = 'Video Preview'

    # Add rich text editor styling for the about field
    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }
        js = ('admin/js/jquery.init.js',)


@admin.register(HotelAmenity)
class HotelAmenityAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'hotel',
        'category',
        'icon',
        'is_featured'
    ]
    list_filter = [
        'category',
        'is_featured',
        'hotel'
    ]
    search_fields = [
        'name',
        'description',
        'hotel__name'
    ]
    list_editable = ['is_featured', 'category']
    list_select_related = ['hotel']
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'hotel',
                'name',
                'category',
                'icon',
                'is_featured'
            )
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )
    ordering = ['hotel', 'category', 'name']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('hotel')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'position',
        'hotel',
        'email',
        'phone',
        'is_active',
        'display_order',
        'photo_tag'
    ]
    list_filter = [
        'is_active',
        'hotel',
        'position'
    ]
    search_fields = [
        'name',
        'position',
        'email',
        'hotel__name'
    ]
    list_editable = [
        'position',
        'is_active',
        'display_order'
    ]
    readonly_fields = ['photo_tag']
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'hotel',
                'name',
                'position',
                'photo',
                'photo_tag'
            )
        }),
        ('Contact Information', {
            'fields': (
                'email',
                'phone'
            )
        }),
        ('Additional Information', {
            'fields': (
                'bio',
            )
        }),
        ('Display Settings', {
            'fields': (
                'display_order',
                'is_active'
            )
        }),
    )
    ordering = ['hotel', 'display_order', 'name']
    list_select_related = ['hotel']

    def photo_tag(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.photo.url)
        return "No Photo"
    photo_tag.short_description = 'Photo'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('hotel')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'event_type',
        'start_date',
        'location',
        'status',
        'is_active',
        'event_image'
    ]

    list_filter = ['event_type', 'status', 'is_active', 'start_date']
    search_fields = ['title', 'description', 'location']
    readonly_fields = ['created_at', 'updated_at', 'event_image_display']

    fieldsets = (
        ('Event Information', {
            'fields': (
                'title',
                'description',
                'event_type',
                'image',
                'event_image_display'
            )
        }),
        ('Schedule', {
            'fields': (
                'start_date',
                'end_date',
            )
        }),
        ('Details', {
            'fields': (
                'location',
                'max_attendees',
                'current_attendees',
                'price',
                'status',
                'is_active',
            )
        }),
        ('Metadata', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at',
            )
        }),
    )

    def event_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return "—"

    event_image.short_description = 'Image'

    def event_image_display(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="300" style="max-height: 200px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image uploaded"

    event_image_display.short_description = 'Image Preview'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'event',
        'email',
        'status',
        'number_of_guests',
        'registration_date',
        'confirmation_sent'
    ]

    list_filter = [
        'status',
        'event',
        'registration_date',
        'confirmation_sent'
    ]

    search_fields = [
        'full_name',
        'email',
        'event__title',
        'company'
    ]

    readonly_fields = [
        'registration_date',
        'confirmation_date'
    ]

    fieldsets = (
        ('Registration Details', {
            'fields': (
                'event',
                'user',
                'full_name',
                'email',
                'phone',
                'company'
            )
        }),
        ('Attendance', {
            'fields': (
                'number_of_guests',
                'special_requirements',
            )
        }),
        ('Status', {
            'fields': (
                'status',
                'confirmation_sent',
                'confirmation_date',
                'registration_date',
            )
        }),
    )

    actions = ['confirm_registrations', 'send_confirmation_emails']

    def confirm_registrations(self, request, queryset):
        updated = queryset.update(status='confirmed', confirmation_date=timezone.now())
        self.message_user(request, f'{updated} registrations confirmed.')

    confirm_registrations.short_description = "Mark selected registrations as confirmed"

    def send_confirmation_emails(self, request, queryset):
        count = 0
        for registration in queryset:
            if not registration.confirmation_sent:
                send_registration_confirmation(registration, request)
                count += 1
        self.message_user(request, f'Confirmation emails sent to {count} registrations.')

    send_confirmation_emails.short_description = "Send confirmation emails"


# Optional: Custom admin site header and title
admin.site.site_header = "Hotel Management System"
admin.site.site_title = "Hotel Admin"
admin.site.index_title = "Welcome to Hotel Management Portal"
from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from .models import RoomType, Room, RoomImage, RoomAmenity


# Inline admins
class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = [
        'image_preview',
        'image',
        'caption',
        'is_featured',
        'display_order'
    ]
    readonly_fields = ['image_preview']
    ordering = ['display_order']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = 'Preview'


class RoomAmenityInline(admin.TabularInline):
    model = RoomAmenity
    extra = 1
    fields = ['name', 'icon']
    ordering = ['name']


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = [
        'room_number',
        'floor',
        'view_description',
        'is_available_badge',
        'special_features_preview'
    ]
    readonly_fields = ['is_available_badge', 'special_features_preview']
    ordering = ['floor', 'room_number']

    def is_available_badge(self, obj):
        if obj.is_available:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: bold;">AVAILABLE</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px; font-weight: bold;">UNAVAILABLE</span>'
        )

    is_available_badge.short_description = 'Status'

    def special_features_preview(self, obj):
        return Truncator(obj.special_features).chars(50)

    special_features_preview.short_description = 'Features'


# Main admin classes
@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'hotel',
        'base_price_display',
        'capacity',
        'size',
        'bed_type',
        'room_count',
        'available_rooms',
        'is_available',
        'display_order',
        'featured_image_preview'
    ]
    list_editable = [
        'display_order',
        'is_available'
    ]
    list_filter = [
        'hotel',
        'is_available',
        'capacity',
        'bed_type'
    ]
    search_fields = [
        'name',
        'description',
        'hotel__name',
        'bed_type'
    ]

    readonly_fields = [
        'featured_image_preview_large',
        'room_type_stats',
        # REMOVED 'slug' from readonly_fields - this was causing the error
    ]
    prepopulated_fields = {'slug': ('name',)}  # This will auto-generate slug from name
    ordering = ['hotel', 'display_order', 'base_price']
    list_select_related = ['hotel']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'hotel',
                'name',
                'slug',  # Keep slug in fieldsets so it's visible
                'description',
                'featured_image',
                'featured_image_preview_large'
            )
        }),
        ('Room Specifications', {
            'fields': (
                'base_price',
                'capacity',
                'size',
                'bed_type'
            )
        }),
        ('Display Settings', {
            'fields': (
                'display_order',
                'is_available'
            )
        }),
        ('Statistics', {
            'classes': ('collapse',),
            'fields': ('room_type_stats',)
        }),
    )

    inlines = [RoomAmenityInline, RoomImageInline, RoomInline]

    def base_price_display(self, obj):
        return format_html(
            '<span style="font-weight: bold; color: #28a745;">GHS {}</span>',
            obj.base_price
        )

    base_price_display.short_description = 'Price'
    base_price_display.admin_order_field = 'base_price'

    def featured_image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.featured_image.url
            )
        return "No Image"

    featured_image_preview.short_description = 'Image'

    def featured_image_preview_large(self, obj):
        if obj.featured_image:
            return format_html(
                '<div style="text-align: center; margin: 15px 0;">'
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: contain; border-radius: 8px; border: 2px solid #e0e0e0;" />'
                '<br><small style="color: #666;">Featured Image</small>'
                '</div>',
                obj.featured_image.url
            )
        return "No Featured Image"

    featured_image_preview_large.short_description = ''

    def room_count(self, obj):
        return obj.rooms.count()

    room_count.short_description = 'Total Rooms'
    room_count.admin_order_field = 'rooms_count'

    def available_rooms(self, obj):
        return obj.rooms.filter(is_available=True).count()

    available_rooms.short_description = 'Available'
    available_rooms.admin_order_field = 'available_count'

    def is_available_badge(self, obj):
        if obj.is_available:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">ACTIVE</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">INACTIVE</span>'
        )

    is_available_badge.short_description = 'Status'
    is_available_badge.admin_order_field = 'is_available'

    def room_type_stats(self, obj):
        total_rooms = obj.rooms.count()
        available_rooms = obj.rooms.filter(is_available=True).count()
        image_count = obj.images.count()
        amenity_count = obj.amenities.count()

        return format_html(
            '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin: 10px 0;">'
            '<h4 style="margin: 0 0 10px 0; color: white;">📊 Room Type Statistics</h4>'
            '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">'
            '<div><strong>Total Rooms:</strong> {}</div>'
            '<div><strong>Available Rooms:</strong> {}</div>'
            '<div><strong>Room Images:</strong> {}</div>'
            '<div><strong>Amenities:</strong> {}</div>'
            '<div><strong>Base Price:</strong> GHS {}</div>'
            '<div><strong>Capacity:</strong> {} guests</div>'
            '</div>'
            '</div>',
            total_rooms, available_rooms, image_count, amenity_count, obj.base_price, obj.capacity
        )

    room_type_stats.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('hotel').prefetch_related('rooms', 'images', 'amenities')

    # Custom actions
    actions = [
        'activate_room_types',
        'deactivate_room_types',
        'update_prices',
        'export_room_types_csv'
    ]

    def activate_room_types(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} room types activated.')

    activate_room_types.short_description = "Activate selected room types"

    def deactivate_room_types(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} room types deactivated.')

    deactivate_room_types.short_description = "Deactivate selected room types"

    def update_prices(self, request, queryset):
        """Update prices by percentage"""
        from django.http import HttpResponseRedirect
        from django.urls import reverse

        # Redirect to a custom form for price updates
        ids = ','.join(str(obj.id) for obj in queryset)
        return HttpResponseRedirect(
            reverse('admin:update_room_prices') + f'?ids={ids}'
        )

    update_prices.short_description = "Update prices for selected"

    def export_room_types_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="room_types_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Name', 'Hotel', 'Base Price', 'Capacity', 'Size', 'Bed Type',
            'Total Rooms', 'Available Rooms', 'Status'
        ])

        for room_type in queryset:
            writer.writerow([
                room_type.name,
                room_type.hotel.name,
                room_type.base_price,
                room_type.capacity,
                room_type.size,
                room_type.bed_type,
                room_type.rooms.count(),
                room_type.rooms.filter(is_available=True).count(),
                'Active' if room_type.is_available else 'Inactive'
            ])

        return response

    export_room_types_csv.short_description = "Export room types to CSV"


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = [
        'room_number',
        'room_type_with_hotel',
        'floor',
        'view_description',
        'is_available',  # Use actual field, not is_available_badge
        'special_features_preview'
    ]
    list_editable = ['is_available']  # Now matches list_display
    list_filter = [
        'room_type__hotel',
        'room_type',
        'floor',
        'is_available'
    ]
    search_fields = [
        'room_number',
        'room_type__name',
        'room_type__hotel__name',
        'view_description',
        'special_features'
    ]

    readonly_fields = ['room_info_card']
    ordering = ['room_type__hotel', 'floor', 'room_number']
    list_select_related = ['room_type', 'room_type__hotel']

    fieldsets = (
        ('Room Identification', {
            'fields': (
                'room_type',
                'room_number',
                'floor'
            )
        }),
        ('Room Features', {
            'fields': (
                'view_description',
                'special_features'
            )
        }),
        ('Availability', {
            'fields': ('is_available',)
        }),
        ('Room Information', {
            'classes': ('collapse',),
            'fields': ('room_info_card',)
        }),
    )

    def room_type_with_hotel(self, obj):
        return f"{obj.room_type.hotel.name} - {obj.room_type.name}"

    room_type_with_hotel.short_description = 'Room Type'
    room_type_with_hotel.admin_order_field = 'room_type__name'

    def is_available_badge(self, obj):
        if obj.is_available:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">AVAILABLE</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">UNAVAILABLE</span>'
        )

    is_available_badge.short_description = 'Status'
    is_available_badge.admin_order_field = 'is_available'

    def special_features_preview(self, obj):
        return Truncator(obj.special_features).chars(60)

    special_features_preview.short_description = 'Special Features'

    def room_info_card(self, obj):
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; margin: 10px 0;">'
            '<strong>Room Information:</strong><br>'
            '<div style="margin-top: 8px; color: #555;">'
            '🏨 <strong>Hotel:</strong> {}<br>'
            '🛏️ <strong>Room Type:</strong> {}<br>'
            '💰 <strong>Base Price:</strong> GHS {}<br>'
            '👥 <strong>Capacity:</strong> {} guests<br>'
            '📏 <strong>Size:</strong> {}<br>'
            '🛌 <strong>Bed Type:</strong> {}'
            '</div>'
            '</div>',
            obj.room_type.hotel.name,
            obj.room_type.name,
            obj.room_type.base_price,
            obj.room_type.capacity,
            obj.room_type.size or 'Not specified',
            obj.room_type.bed_type or 'Not specified'
        )

    room_info_card.short_description = ''

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('room_type__hotel')

    # Custom actions
    actions = [
        'mark_rooms_available',
        'mark_rooms_unavailable',
        'export_rooms_csv'
    ]

    def mark_rooms_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} rooms marked as available.')

    mark_rooms_available.short_description = "Mark selected as available"

    def mark_rooms_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} rooms marked as unavailable.')

    mark_rooms_unavailable.short_description = "Mark selected as unavailable"


@admin.register(RoomImage)
class RoomImageAdmin(admin.ModelAdmin):
    list_display = [
        'image_preview',
        'room_type_with_hotel',
        'caption',
        'is_featured',  # Use actual field, not is_featured_badge
        'display_order'
    ]
    list_editable = [
        'caption',
        'is_featured',  # Now matches list_display
        'display_order'
    ]
    list_filter = [
        'room_type__hotel',
        'room_type',
        'is_featured'
    ]
    search_fields = [
        'caption',
        'room_type__name',
        'room_type__hotel__name'
    ]

    readonly_fields = ['image_preview_large']
    ordering = ['room_type', 'display_order']
    list_select_related = ['room_type', 'room_type__hotel']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = 'Image'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<div style="text-align: center; margin: 15px 0;">'
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: contain; border-radius: 8px; border: 2px solid #e0e0e0;" />'
                '<br><small style="color: #666;">Room Image</small>'
                '</div>',
                obj.image.url
            )
        return "No Image"

    image_preview_large.short_description = ''

    def room_type_with_hotel(self, obj):
        return f"{obj.room_type.hotel.name} - {obj.room_type.name}"

    room_type_with_hotel.short_description = 'Room Type'
    room_type_with_hotel.admin_order_field = 'room_type__name'

    def is_featured_badge(self, obj):
        if obj.is_featured:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">⭐ FEATURED</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">Standard</span>'
        )

    is_featured_badge.short_description = 'Featured'


@admin.register(RoomAmenity)
class RoomAmenityAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'room_type_with_hotel',
        'icon_display'
    ]
    list_filter = [
        'room_type__hotel',
        'room_type'
    ]
    search_fields = [
        'name',
        'icon',
        'room_type__name',
        'room_type__hotel__name'
    ]
    list_select_related = ['room_type', 'room_type__hotel']
    ordering = ['room_type', 'name']

    def room_type_with_hotel(self, obj):
        return f"{obj.room_type.hotel.name} - {obj.room_type.name}"

    room_type_with_hotel.short_description = 'Room Type'
    room_type_with_hotel.admin_order_field = 'room_type__name'

    def icon_display(self, obj):
        if obj.icon:
            return format_html(
                '<span style="font-size: 16px;" title="{}">{}</span>',
                obj.icon, obj.icon
            )
        return "—"

    icon_display.short_description = 'Icon'


# Custom filters
from django.contrib.admin import SimpleListFilter


class HotelFilter(SimpleListFilter):
    title = 'hotel'
    parameter_name = 'hotel'

    def lookups(self, request, model_admin):
        from hotel.models import Hotel
        return [(h.id, h.name) for h in Hotel.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(room_type__hotel_id=self.value())


# Add hotel filter to relevant admins
RoomAdmin.list_filter.append(HotelFilter)
RoomImageAdmin.list_filter.append(HotelFilter)
RoomAmenityAdmin.list_filter.append(HotelFilter)
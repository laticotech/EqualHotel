from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from .models import Service, ServiceReservation, ServiceReservationPayment


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category_badge',
        'price_display',
        'availability_display',
        'requires_booking_badge',
        'is_active',
        'display_order',
        'image_preview'
    ]
    list_editable = [
        'display_order',
        'is_active'
    ]
    list_filter = [
        'category',
        'is_free',
        'requires_booking',
        'is_active',
        'available_days'
    ]
    search_fields = [
        'name',
        'description',
        'available_days',
        'available_times'
    ]

    readonly_fields = [
        'image_preview_large',
        'service_summary',
        'pricing_info'
    ]
    ordering = ['display_order', 'name']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name',
                'category',
                'description',
                'image',
                'image_preview_large',
                'icon'
            )
        }),
        ('Pricing', {
            'fields': (
                'pricing_info',
                'is_free',
                'price'
            )
        }),
        ('Availability', {
            'fields': (
                'available_days',
                'available_times',
                'requires_booking'
            )
        }),
        ('Display Settings', {
            'fields': (
                'display_order',
                'is_active'
            )
        }),
        ('Service Summary', {
            'classes': ('collapse',),
            'fields': ('service_summary',)
        }),
    )

    def category_badge(self, obj):
        category_colors = {
            'dining': '#e74c3c',
            'spa': '#9b59b6',
            'business': '#3498db',
            'recreation': '#2ecc71',
            'transport': '#f39c12',
            'other': '#95a5a6'
        }
        color = category_colors.get(obj.category, '#666')

        category_icons = {
            'dining': '🍽️',
            'spa': '💆',
            'business': '💼',
            'recreation': '🎯',
            'transport': '🚗',
            'other': '🔧'
        }
        icon = category_icons.get(obj.category, '📋')

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{} {}</span>',
            color, icon, obj.get_category_display().upper()
        )

    category_badge.short_description = 'Category'
    category_badge.admin_order_field = 'category'

    def price_display(self, obj):
        if obj.is_free:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">FREE</span>'
            )
        elif obj.price:
            return format_html(
                '<span style="font-weight: bold; color: #e74c3c;">GHS {}</span>',
                obj.price
            )
        return format_html(
            '<span style="color: #6c757d; font-style: italic;">Price on request</span>'
        )

    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'

    def availability_display(self, obj):
        days = obj.available_days or 'Not specified'
        times = obj.available_times or 'Not specified'

        return format_html(
            '<div style="font-size: 11px; line-height: 1.3;">'
            '<strong>📅</strong> {}<br>'
            '<strong>🕒</strong> {}'
            '</div>',
            days, times
        )

    availability_display.short_description = 'Availability'

    def requires_booking_badge(self, obj):
        if obj.requires_booking:
            return format_html(
                '<span style="background-color: #17a2b8; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">📞 BOOKING REQUIRED</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">WALK-IN</span>'
        )

    requires_booking_badge.short_description = 'Booking'
    requires_booking_badge.admin_order_field = 'requires_booking'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        elif obj.icon:
            return format_html(
                '<div style="width: 50px; height: 50px; background: #f8f9fa; display: flex; align-items: center; justify-content: center; border-radius: 4px; border: 1px solid #ddd; font-size: 20px;">{}</div>',
                obj.icon
            )
        return format_html(
            '<div style="width: 50px; height: 50px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; border-radius: 4px; border: 1px solid #ddd; color: #999; font-size: 10px;">No Image</div>'
        )

    image_preview.short_description = 'Image/Icon'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<div style="text-align: center; margin: 15px 0;">'
                '<img src="{}" style="max-width: 300px; max-height: 200px; object-fit: contain; border-radius: 8px; border: 2px solid #e0e0e0;" />'
                '<br><small style="color: #666;">Service Image</small>'
                '</div>',
                obj.image.url
            )
        elif obj.icon:
            return format_html(
                '<div style="text-align: center; margin: 15px 0; padding: 20px; background: #f8f9fa; border-radius: 8px;">'
                '<div style="font-size: 48px; margin-bottom: 10px;">{}</div>'
                '<small style="color: #666;">Service Icon</small>'
                '</div>',
                obj.icon
            )
        return "No image or icon available"

    image_preview_large.short_description = ''

    def pricing_info(self, obj):
        if obj.is_free:
            return format_html(
                '<div style="background: #d4edda; color: #155724; padding: 12px; border-radius: 6px; border-left: 4px solid #28a745; margin: 10px 0;">'
                '<strong>💰 Pricing: FREE SERVICE</strong><br>'
                '<small>This service is provided free of charge to guests.</small>'
                '</div>'
            )
        elif obj.price:
            return format_html(
                '<div style="background: #fff3cd; color: #856404; padding: 12px; border-radius: 6px; border-left: 4px solid #ffc107; margin: 10px 0;">'
                '<strong>💰 Pricing: GHS {}</strong><br>'
                '<small>Standard price for this service.</small>'
                '</div>',
                obj.price
            )
        return format_html(
            '<div style="background: #d1ecf1; color: #0c5460; padding: 12px; border-radius: 6px; border-left: 4px solid #17a2b8; margin: 10px 0;">'
            '<strong>💰 Pricing: ON REQUEST</strong><br>'
            '<small>Contact for pricing information.</small>'
            '</div>'
        )

    pricing_info.short_description = ''

    def service_summary(self, obj):
        icon_display = obj.icon if obj.icon else "No icon"
        booking_type = "Booking Required" if obj.requires_booking else "Walk-in Available"
        status = "Active" if obj.is_active else "Inactive"

        return format_html(
            '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin: 10px 0;">'
            '<h4 style="margin: 0 0 10px 0; color: white;">📊 Service Summary</h4>'
            '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">'
            '<div><strong>Category:</strong> {}</div>'
            '<div><strong>Icon:</strong> {}</div>'
            '<div><strong>Pricing:</strong> {}</div>'
            '<div><strong>Booking:</strong> {}</div>'
            '<div><strong>Availability:</strong> {}</div>'
            '<div><strong>Status:</strong> {}</div>'
            '<div><strong>Display Order:</strong> {}</div>'
            '</div>'
            '</div>',
            obj.get_category_display(),
            icon_display,
            "Free" if obj.is_free else f"GHS {obj.price}" if obj.price else "On Request",
            booking_type,
            obj.available_days or "Not specified",
            status,
            obj.display_order
        )

    service_summary.short_description = ''

    # Custom actions
    actions = [
        'activate_services',
        'deactivate_services',
        'mark_as_free',
        'mark_as_paid',
        'require_booking',
        'remove_booking_requirement',
        'export_services_csv'
    ]

    def activate_services(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} services activated.')

    activate_services.short_description = "Activate selected services"

    def deactivate_services(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} services deactivated.')

    deactivate_services.short_description = "Deactivate selected services"

    def mark_as_free(self, request, queryset):
        updated = queryset.update(is_free=True, price=None)
        self.message_user(request, f'{updated} services marked as free.')

    mark_as_free.short_description = "Mark selected as free services"

    def mark_as_paid(self, request, queryset):
        updated = queryset.update(is_free=False)
        self.message_user(request, f'{updated} services marked as paid services.')

    mark_as_paid.short_description = "Mark selected as paid services"

    def require_booking(self, request, queryset):
        updated = queryset.update(requires_booking=True)
        self.message_user(request, f'{updated} services now require booking.')

    require_booking.short_description = "Require booking for selected"

    def remove_booking_requirement(self, request, queryset):
        updated = queryset.update(requires_booking=False)
        self.message_user(request, f'{updated} services no longer require booking.')

    remove_booking_requirement.short_description = "Remove booking requirement"

    def export_services_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="services_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Name', 'Category', 'Description', 'Price', 'Free',
            'Available Days', 'Available Times', 'Requires Booking',
            'Display Order', 'Status'
        ])

        for service in queryset:
            writer.writerow([
                service.name,
                service.get_category_display(),
                service.description[:300],
                service.price if service.price else '',
                'Yes' if service.is_free else 'No',
                service.available_days,
                service.available_times,
                'Yes' if service.requires_booking else 'No',
                service.display_order,
                'Active' if service.is_active else 'Inactive'
            ])

        return response

    export_services_csv.short_description = "Export services to CSV"

    # Auto-generate icon if empty based on category
    def save_model(self, request, obj, form, change):
        if not obj.icon:
            category_icons = {
                'dining': '🍽️',
                'spa': '💆',
                'business': '💼',
                'recreation': '🎯',
                'transport': '🚗',
                'other': '🔧'
            }
            obj.icon = category_icons.get(obj.category, '📋')
        super().save_model(request, obj, form, change)

    # Add the changelist_view method directly to ServiceAdmin
    def changelist_view(self, request, extra_context=None):
        from django.db.models import Count, Q

        stats = {
            'total_services': Service.objects.count(),
            'active_services': Service.objects.filter(is_active=True).count(),
            'free_services': Service.objects.filter(is_free=True).count(),
            'paid_services': Service.objects.filter(is_free=False, price__isnull=False).count(),
            'booking_required': Service.objects.filter(requires_booking=True).count(),
            'services_by_category': Service.objects.values('category').annotate(
                count=Count('id')
            ).order_by('-count')
        }

        extra_context = extra_context or {}
        extra_context['stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)


# Custom filters
from django.contrib.admin import SimpleListFilter


class PriceTypeFilter(SimpleListFilter):
    title = 'price type'
    parameter_name = 'price_type'

    def lookups(self, request, model_admin):
        return (
            ('free', 'Free Services'),
            ('paid', 'Paid Services'),
            ('price_on_request', 'Price on Request'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'free':
            return queryset.filter(is_free=True)
        elif self.value() == 'paid':
            return queryset.filter(is_free=False, price__isnull=False)
        elif self.value() == 'price_on_request':
            return queryset.filter(is_free=False, price__isnull=True)


class BookingRequirementFilter(SimpleListFilter):
    title = 'booking requirement'
    parameter_name = 'booking'

    def lookups(self, request, model_admin):
        return (
            ('requires_booking', 'Requires Booking'),
            ('walk_in', 'Walk-in Allowed'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'requires_booking':
            return queryset.filter(requires_booking=True)
        elif self.value() == 'walk_in':
            return queryset.filter(requires_booking=False)


@admin.register(ServiceReservation)
class ServiceReservationAdmin(admin.ModelAdmin):
    list_display = [
        'reservation_number',
        'guest_name_badge',
        'service_with_category',
        'reservation_datetime',
        'number_of_guests',
        'total_amount_display',
        'payment_status_badge',
        'status_badge',
        'created_at'
    ]
    list_filter = [
        'status',
        'reservation_date',
        'service',
        'service__category',
        'created_at'
    ]
    search_fields = [
        'reservation_number',
        'guest_name',
        'guest_email',
        'guest_phone',
        'service__name'
    ]
    readonly_fields = [
        'reservation_number',
        'created_at',
        'updated_at',
        'payment_info',
        'reservation_summary'
    ]
    date_hierarchy = 'reservation_date'
    ordering = ['-reservation_date', '-reservation_time']

    fieldsets = (
        ('Reservation Information', {
            'fields': (
                'reservation_number',
                'service',
                'status',
                'reservation_summary'
            )
        }),
        ('Guest Details', {
            'fields': (
                'guest_name',
                'guest_email',
                'guest_phone'
            )
        }),
        ('Reservation Details', {
            'fields': (
                'reservation_date',
                'reservation_time',
                'number_of_guests',
                'special_requests'
            )
        }),
        ('Payment Information', {
            'fields': ('payment_info',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def guest_name_badge(self, obj):
        return format_html(
            '<div style="font-weight: bold;">{}</div>'
            '<div style="font-size: 11px; color: #666;">{}</div>',
            obj.guest_name,
            obj.guest_email
        )

    guest_name_badge.short_description = 'Guest'
    guest_name_badge.admin_order_field = 'guest_name'

    def service_with_category(self, obj):
        category_colors = {
            'dining': '#e74c3c',
            'spa': '#9b59b6',
            'business': '#3498db',
            'recreation': '#2ecc71',
            'transport': '#f39c12',
            'other': '#95a5a6'
        }
        color = category_colors.get(obj.service.category, '#666')

        return format_html(
            '<div style="font-weight: bold;">{}</div>'
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 10px;">{}</span>',
            obj.service.name,
            color,
            obj.service.get_category_display()
        )

    service_with_category.short_description = 'Service'
    service_with_category.admin_order_field = 'service__name'

    def reservation_datetime(self, obj):
        return format_html(
            '<div style="font-weight: bold;">{}</div>'
            '<div style="font-size: 11px; color: #666;">{}</div>',
            obj.reservation_date.strftime('%b %d, %Y'),
            obj.reservation_time.strftime('%I:%M %p')
        )

    reservation_datetime.short_description = 'Date & Time'
    reservation_datetime.admin_order_field = 'reservation_date'

    def total_amount_display(self, obj):
        if obj.total_amount > 0:
            return format_html(
                '<span style="font-weight: bold; color: #e74c3c;">GHS {}</span>',
                obj.total_amount
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">FREE</span>'
        )

    total_amount_display.short_description = 'Amount'
    total_amount_display.admin_order_field = 'service__price'

    def payment_status_badge(self, obj):
        status_colors = {
            'completed': '#28a745',
            'pending': '#ffc107',
            'failed': '#dc3545',
            'refunded': '#6c757d',
            'no_payment_required': '#17a2b8'
        }
        color = status_colors.get(obj.payment_status, '#6c757d')

        status_text = obj.payment_status.replace('_', ' ').title()

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, status_text
        )

    payment_status_badge.short_description = 'Payment'
    payment_status_badge.admin_order_field = 'payment__payment_status'

    def status_badge(self, obj):
        status_colors = {
            'confirmed': '#28a745',
            'pending': '#ffc107',
            'cancelled': '#dc3545',
            'completed': '#17a2b8'
        }
        color = status_colors.get(obj.status, '#6c757d')

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display().upper()
        )

    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def payment_info(self, obj):
        if hasattr(obj, 'payment'):
            payment = obj.payment
            return format_html(
                '<div style="background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #007bff;">'
                '<h4 style="margin: 0 0 10px 0;">💳 Payment Details</h4>'
                '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">'
                '<div><strong>Payment Method:</strong> {}</div>'
                '<div><strong>Amount Paid:</strong> GHS {}</div>'
                '<div><strong>Expected Amount:</strong> GHS {}</div>'
                '<div><strong>Balance Due:</strong> GHS {}</div>'
                '<div><strong>Transaction ID:</strong> {}</div>'
                '<div><strong>Payment Reference:</strong> {}</div>'
                '<div><strong>Payment Date:</strong> {}</div>'
                '</div>'
                '</div>',
                payment.get_payment_method_display(),
                payment.amount_paid,
                payment.amount_expected,
                payment.balance_due,
                payment.transaction_id or 'N/A',
                payment.payment_reference,
                payment.payment_date.strftime('%b %d, %Y %I:%M %p') if payment.payment_date else 'N/A'
            )
        elif obj.requires_payment:
            return format_html(
                '<div style="background: #fff3cd; color: #856404; padding: 12px; border-radius: 6px; border-left: 4px solid #ffc107;">'
                '<strong>⚠️ Payment Required</strong><br>'
                '<small>Expected amount: GHS {}. No payment record created yet.</small>'
                '</div>',
                obj.total_amount
            )
        return format_html(
            '<div style="background: #d4edda; color: #155724; padding: 12px; border-radius: 6px; border-left: 4px solid #28a745;">'
            '<strong>✅ No Payment Required</strong><br>'
            '<small>This is a free service.</small>'
            '</div>'
        )

    payment_info.short_description = ''

    def reservation_summary(self, obj):
        return format_html(
            '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin: 10px 0;">'
            '<h4 style="margin: 0 0 10px 0; color: white;">📊 Reservation Summary</h4>'
            '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">'
            '<div><strong>Service:</strong> {}</div>'
            '<div><strong>Category:</strong> {}</div>'
            '<div><strong>Guests:</strong> {}</div>'
            '<div><strong>Total Amount:</strong> GHS {}</div>'
            '<div><strong>Payment Status:</strong> {}</div>'
            '<div><strong>Reservation Status:</strong> {}</div>'
            '<div><strong>Created:</strong> {}</div>'
            '<div><strong>Last Updated:</strong> {}</div>'
            '</div>'
            '</div>',
            obj.service.name,
            obj.service.get_category_display(),
            obj.number_of_guests,
            obj.total_amount,
            obj.payment_status.replace('_', ' ').title(),
            obj.get_status_display(),
            obj.created_at.strftime('%b %d, %Y %I:%M %p'),
            obj.updated_at.strftime('%b %d, %Y %I:%M %p')
        )

    reservation_summary.short_description = ''

    # Custom actions
    actions = [
        'confirm_reservations',
        'cancel_reservations',
        'mark_as_completed',
        'create_payment_records'
    ]

    def confirm_reservations(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} reservations confirmed.')

    confirm_reservations.short_description = "Confirm selected reservations"

    def cancel_reservations(self, request, queryset):
        updated = queryset.exclude(status='cancelled').update(status='cancelled')
        self.message_user(request, f'{updated} reservations cancelled.')

    cancel_reservations.short_description = "Cancel selected reservations"

    def mark_as_completed(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='completed')
        self.message_user(request, f'{updated} reservations marked as completed.')

    mark_as_completed.short_description = "Mark selected as completed"

    def create_payment_records(self, request, queryset):
        created = 0
        for reservation in queryset:
            if reservation.requires_payment and not hasattr(reservation, 'payment'):
                ServiceReservationPayment.objects.create(
                    service_reservation=reservation,
                    amount_expected=reservation.total_amount
                )
                created += 1
        self.message_user(request, f'{created} payment records created.')

    create_payment_records.short_description = "Create payment records for selected"


@admin.register(ServiceReservationPayment)
class ServiceReservationPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_reference',
        'reservation_link',
        'guest_name',
        'amount_expected',
        'amount_paid',
        'balance_due_display',
        'payment_method_badge',
        'payment_status_badge',
        'payment_date'
    ]
    list_filter = [
        'payment_status',
        'payment_method',
        'payment_date'
    ]
    search_fields = [
        'payment_reference',
        'transaction_id',
        'service_reservation__reservation_number',
        'service_reservation__guest_name',
        'service_reservation__guest_email'
    ]
    readonly_fields = [
        'payment_reference',
        'payment_details_summary',
        'get_balance_due'  # Changed from 'balance_due' to a method
    ]
    list_editable = ['amount_paid']  # Removed 'payment_status' from list_editable since it's not in list_display
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']  # Use payment_date instead of created_at

    fieldsets = (
        ('Payment Information', {
            'fields': (
                'payment_reference',
                'service_reservation',
                'payment_details_summary'
            )
        }),
        ('Payment Details', {
            'fields': (
                'payment_method',
                'amount_expected',
                'amount_paid',
                'get_balance_due',  # Changed from 'balance_due'
                'payment_status',
                'transaction_id',
                'payment_date'
            )
        }),
        ('Additional Information', {
            'fields': ('payment_notes',),
            'classes': ('collapse',)
        })
    )

    def reservation_link(self, obj):
        return format_html(
            '<a href="{}" style="font-weight: bold;">{}</a>'
            '<div style="font-size: 11px; color: #666;">{}</div>',
            f'../servicereservation/{obj.service_reservation.id}/change/',
            obj.service_reservation.reservation_number,
            obj.service_reservation.service.name
        )

    reservation_link.short_description = 'Reservation'
    reservation_link.admin_order_field = 'service_reservation__reservation_number'

    def guest_name(self, obj):
        return format_html(
            '<div style="font-weight: bold;">{}</div>'
            '<div style="font-size: 11px; color: #666;">{}</div>',
            obj.service_reservation.guest_name,
            obj.service_reservation.guest_email
        )

    guest_name.short_description = 'Guest'
    guest_name.admin_order_field = 'service_reservation__guest_name'

    def balance_due_display(self, obj):
        balance = obj.balance_due
        if balance == 0:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">PAID</span>'
            )
        elif balance > 0:
            return format_html(
                '<span style="background-color: #ffc107; color: #212529; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">GHS {}</span>',
                balance
            )
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">OVERPAID</span>'
        )

    balance_due_display.short_description = 'Balance'

    def get_balance_due(self, obj):
        """Method to display balance due in readonly fields"""
        return f"GHS {obj.balance_due}"

    get_balance_due.short_description = 'Balance Due'

    def payment_method_badge(self, obj):
        method_colors = {
            'paystack': '#0055ff',
            'flutterwave': '#f5a623',
            'cash': '#28a745',
            'bank_transfer': '#6c757d'
        }
        color = method_colors.get(obj.payment_method, '#6c757d')

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_payment_method_display().upper()
        )

    payment_method_badge.short_description = 'Method'
    payment_method_badge.admin_order_field = 'payment_method'

    def payment_status_badge(self, obj):
        status_colors = {
            'completed': '#28a745',
            'pending': '#ffc107',
            'failed': '#dc3545',
            'refunded': '#6c757d'
        }
        color = status_colors.get(obj.payment_status, '#6c757d')

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_payment_status_display().upper()
        )

    payment_status_badge.short_description = 'Status'
    payment_status_badge.admin_order_field = 'payment_status'

    def payment_details_summary(self, obj):
        return format_html(
            '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin: 10px 0;">'
            '<h4 style="margin: 0 0 10px 0; color: white;">💰 Payment Summary</h4>'
            '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">'
            '<div><strong>Reservation:</strong> {}</div>'
            '<div><strong>Guest:</strong> {}</div>'
            '<div><strong>Service:</strong> {}</div>'
            '<div><strong>Expected Amount:</strong> GHS {}</div>'
            '<div><strong>Amount Paid:</strong> GHS {}</div>'
            '<div><strong>Balance Due:</strong> GHS {}</div>'
            '<div><strong>Payment Method:</strong> {}</div>'
            '<div><strong>Status:</strong> {}</div>'
            '</div>'
            '</div>',
            obj.service_reservation.reservation_number,
            obj.service_reservation.guest_name,
            obj.service_reservation.service.name,
            obj.amount_expected,
            obj.amount_paid,
            obj.balance_due,
            obj.get_payment_method_display(),
            obj.get_payment_status_display()
        )

    payment_details_summary.short_description = ''

    # Custom actions
    actions = [
        'mark_as_completed',
        'mark_as_pending',
        'mark_as_failed',
        'process_refunds'
    ]

    def mark_as_completed(self, request, queryset):
        for payment in queryset:
            payment.mark_as_paid()
        self.message_user(request, f'{queryset.count()} payments marked as completed.')

    mark_as_completed.short_description = "Mark selected as completed"

    def mark_as_pending(self, request, queryset):
        updated = queryset.update(payment_status='pending')
        self.message_user(request, f'{updated} payments marked as pending.')

    mark_as_pending.short_description = "Mark selected as pending"

    def mark_as_failed(self, request, queryset):
        updated = queryset.update(payment_status='failed')
        self.message_user(request, f'{updated} payments marked as failed.')

    mark_as_failed.short_description = "Mark selected as failed"

    def process_refunds(self, request, queryset):
        updated = queryset.update(payment_status='refunded')
        self.message_user(request, f'{updated} payments marked as refunded.')

    process_refunds.short_description = "Process refunds for selected"


# Add custom filters to ServiceAdmin
ServiceAdmin.list_filter.extend([PriceTypeFilter, BookingRequirementFilter])
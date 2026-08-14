from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Booking, BookingPayment


# Inline admin for payments
class BookingPaymentInline(admin.StackedInline):
    model = BookingPayment
    extra = 0
    max_num = 1
    can_delete = False
    fields = [
        'payment_method',
        'amount_paid',
        'payment_status',
        'transaction_id',
        'payment_date'
    ]
    readonly_fields = ['payment_date']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_reference',
        'guest_name',
        'room_info',
        'check_in',
        'check_out',
        'nights',
        'total_price',
        'status',  # Use actual field, not status_badge
        'created_at',
        'payment_status'
    ]
    list_editable = ['status']
    list_filter = [
        'status',
        'check_in',
        'check_out',
        'created_at',
        'room__room_type__hotel'
    ]
    search_fields = [
        'booking_reference',
        'guest_name',
        'guest_email',
        'guest_phone',
        'room__room_number',
        'room__room_type__name'
    ]

    readonly_fields = [
        'booking_reference',
        'created_at',
        'updated_at',
        'nights',
        'total_amount_paid',
        'payment_status_display'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    list_select_related = ['room', 'room__room_type', 'room__room_type__hotel']

    fieldsets = (
        ('Booking Information', {
            'fields': (
                'booking_reference',
                'room',
                'check_in',
                'check_out',
                'nights',
                'adults',
                'children',
                'total_price'
            )
        }),
        ('Guest Information', {
            'fields': (
                'guest_name',
                'guest_email',
                'guest_phone',
                'guest_address',
                'special_requests'
            )
        }),
        ('Status & Payment', {
            'fields': (
                'status',
                'payment_status_display',
                'total_amount_paid'
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

    inlines = [BookingPaymentInline]

    def room_info(self, obj):
        return f"{obj.room.room_type.name} - Room {obj.room.room_number}"

    room_info.short_description = 'Room'
    room_info.admin_order_field = 'room__room_number'

    def status_badge(self, obj):
        status_colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'checked_in': 'green',
            'checked_out': 'gray',
            'cancelled': 'red',
            'no_show': 'darkred'
        }
        color = status_colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_status_display().upper()
        )

    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def payment_status_display(self, obj):
        if hasattr(obj, 'payment'):
            status_colors = {
                'pending': 'orange',
                'completed': 'green',
                'failed': 'red',
                'refunded': 'blue'
            }
            color = status_colors.get(obj.payment.payment_status, 'gray')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{} - GHS {}</span>',
                color, obj.payment.get_payment_status_display(), obj.payment.amount_paid
            )
        return format_html(
            '<span style="background-color: red; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">NO PAYMENT</span>'
        )

    payment_status_display.short_description = 'Payment Status'

    def total_amount_paid(self, obj):
        if hasattr(obj, 'payment'):
            return f"GHS {obj.payment.amount_paid}"
        return "GHS 0.00"

    total_amount_paid.short_description = 'Amount Paid'

    def payment_status(self, obj):
        if hasattr(obj, 'payment'):
            return obj.payment.get_payment_status_display()
        return "No Payment"

    payment_status.short_description = 'Payment'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'room',
            'room__room_type',
            'room__room_type__hotel'
        ).prefetch_related('payment')

    # Custom actions
    actions = [
        'mark_as_confirmed',
        'mark_as_checked_in',
        'mark_as_checked_out',
        'mark_as_cancelled',
        'generate_checkin_report'
    ]

    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} bookings marked as confirmed.')

    mark_as_confirmed.short_description = "Mark selected as confirmed"

    def mark_as_checked_in(self, request, queryset):
        updated = queryset.update(status='checked_in')
        self.message_user(request, f'{updated} bookings marked as checked in.')

    mark_as_checked_in.short_description = "Mark selected as checked in"

    def mark_as_checked_out(self, request, queryset):
        updated = queryset.update(status='checked_out')
        self.message_user(request, f'{updated} bookings marked as checked out.')

    mark_as_checked_out.short_description = "Mark selected as checked out"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} bookings marked as cancelled.')

    mark_as_cancelled.short_description = "Mark selected as cancelled"

    def generate_checkin_report(self, request, queryset):
        """Generate a simple check-in report"""
        today = timezone.now().date()
        upcoming = queryset.filter(check_in__gte=today, status='confirmed')

        report = f"Check-in Report generated on {today}\n\n"
        report += f"Total selected bookings: {queryset.count()}\n"
        report += f"Upcoming check-ins: {upcoming.count()}\n\n"

        for booking in upcoming:
            report += f"- {booking.guest_name} (Room {booking.room.room_number}) - {booking.check_in}\n"

        self.message_user(request, format_html('<pre>{}</pre>', report))

    generate_checkin_report.short_description = "Generate check-in report"


@admin.register(BookingPayment)
class BookingPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id',
        'booking_reference',
        'guest_name',
        'payment_method',
        'amount_paid',
        'payment_status',  # Use actual field, not payment_status_badge
        'payment_date'
    ]
    list_editable = ['payment_status']
    list_filter = [
        'payment_status',
        'payment_method',
        'payment_date'
    ]
    search_fields = [
        'transaction_id',
        'booking__booking_reference',
        'booking__guest_name',
        'booking__guest_email'
    ]

    readonly_fields = [
        'payment_date',
        'booking_link'
    ]
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']
    list_select_related = ['booking']

    fieldsets = (
        ('Payment Information', {
            'fields': (
                'booking_link',
                'payment_method',
                'amount_paid',
                'payment_status',
                'transaction_id'
            )
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('payment_date',)
        }),
    )

    def booking_reference(self, obj):
        return obj.booking.booking_reference

    booking_reference.short_description = 'Booking Ref'
    booking_reference.admin_order_field = 'booking__booking_reference'

    def guest_name(self, obj):
        return obj.booking.guest_name

    guest_name.short_description = 'Guest'
    guest_name.admin_order_field = 'booking__guest_name'

    def payment_status_badge(self, obj):
        status_colors = {
            'pending': 'orange',
            'completed': 'green',
            'failed': 'red',
            'refunded': 'blue'
        }
        color = status_colors.get(obj.payment_status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_payment_status_display().upper()
        )

    payment_status_badge.short_description = 'Status'

    def booking_link(self, obj):
        url = f"/admin/bookings/booking/{obj.booking.id}/change/"
        return format_html(
            '<a href="{}" style="font-weight: bold; color: #007bff;">{} - {}</a>',
            url, obj.booking.booking_reference, obj.booking.guest_name
        )

    booking_link.short_description = 'Booking'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('booking')

    # Custom actions for payments
    actions = [
        'mark_payments_completed',
        'mark_payments_failed',
        'export_payments_csv'
    ]

    def mark_payments_completed(self, request, queryset):
        updated = queryset.update(payment_status='completed')
        self.message_user(request, f'{updated} payments marked as completed.')

    mark_payments_completed.short_description = "Mark selected as completed"

    def mark_payments_failed(self, request, queryset):
        updated = queryset.update(payment_status='failed')
        self.message_user(request, f'{updated} payments marked as failed.')

    mark_payments_failed.short_description = "Mark selected as failed"

    def export_payments_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payments_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Transaction ID', 'Booking Reference', 'Guest Name',
            'Payment Method', 'Amount', 'Status', 'Payment Date'
        ])

        for payment in queryset:
            writer.writerow([
                payment.transaction_id,
                payment.booking.booking_reference,
                payment.booking.guest_name,
                payment.get_payment_method_display(),
                payment.amount_paid,
                payment.get_payment_status_display(),
                payment.payment_date.strftime('%Y-%m-%d %H:%M')
            ])

        return response

    export_payments_csv.short_description = "Export selected payments to CSV"


# Custom filters
from django.contrib.admin import SimpleListFilter


class PaymentStatusFilter(SimpleListFilter):
    title = 'payment status'
    parameter_name = 'has_payment'

    def lookups(self, request, model_admin):
        return (
            ('has_payment', 'Has Payment'),
            ('no_payment', 'No Payment'),
            ('completed', 'Payment Completed'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'has_payment':
            return queryset.filter(payment__isnull=False)
        if self.value() == 'no_payment':
            return queryset.filter(payment__isnull=True)
        if self.value() == 'completed':
            return queryset.filter(payment__payment_status='completed')


# Add custom filter to BookingAdmin
BookingAdmin.list_filter.append(PaymentStatusFilter)
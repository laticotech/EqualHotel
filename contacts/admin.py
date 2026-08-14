from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactInquiry, NewsletterSubscriber


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = [
        'subject',
        'name',
        'email',
        'inquiry_type_badge',
        'phone',
        'is_resolved',  # Use actual field, not is_resolved_badge
        'created_at',
        'message_preview'
    ]
    list_editable = ['is_resolved']  # Now matches list_display
    list_filter = [
        'inquiry_type',
        'is_resolved',
        'created_at'
    ]
    search_fields = [
        'name',
        'email',
        'phone',
        'subject',
        'message'
    ]

    readonly_fields = [
        'created_at',
        'message_preview_detailed',
        'contact_info'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Contact Information', {
            'fields': (
                'contact_info',
                'name',
                'email',
                'phone',
            )
        }),
        ('Inquiry Details', {
            'fields': (
                'inquiry_type',
                'subject',
                'message_preview_detailed',
                'message',
            )
        }),
        ('Resolution Status', {
            'fields': (
                'is_resolved',
                'resolved_notes',
            )
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': ('created_at',)
        }),
    )

    def inquiry_type_badge(self, obj):
        type_colors = {
            'general': 'blue',
            'booking': 'green',
            'group': 'purple',
            'event': 'orange',
            'complaint': 'red',
            'suggestion': 'teal'
        }
        color = type_colors.get(obj.inquiry_type, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_inquiry_type_display().upper()
        )

    inquiry_type_badge.short_description = 'Type'
    inquiry_type_badge.admin_order_field = 'inquiry_type'

    def is_resolved_badge(self, obj):
        if obj.is_resolved:
            return format_html(
                '<span style="background-color: green; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">✓ RESOLVED</span>'
            )
        return format_html(
            '<span style="background-color: orange; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">⏳ PENDING</span>'
        )

    is_resolved_badge.short_description = 'Status'
    is_resolved_badge.admin_order_field = 'is_resolved'

    def message_preview(self, obj):
        return Truncator(obj.message).chars(80)

    message_preview.short_description = 'Message Preview'

    def message_preview_detailed(self, obj):
        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; margin: 10px 0;">'
            '<strong>Message Preview:</strong><br>'
            '<div style="margin-top: 8px; color: #555;">{}</div>'
            '</div>',
            obj.message.replace('\n', '<br>')
        )

    message_preview_detailed.short_description = ''

    def contact_info(self, obj):
        phone_display = f" | 📞 {obj.phone}" if obj.phone else ""
        return format_html(
            '<div style="background: #e8f5e8; padding: 10px; border-radius: 5px; margin: 10px 0;">'
            '<strong>👤 {}</strong> | 📧 {} {}'
            '</div>',
            obj.name, obj.email, phone_display
        )

    contact_info.short_description = 'Contact Summary'

    # Custom actions
    actions = [
        'mark_as_resolved',
        'mark_as_unresolved',
        'send_response_email',
        'export_inquiries_csv'
    ]

    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True)
        self.message_user(request, f'{updated} inquiries marked as resolved.')

    mark_as_resolved.short_description = "Mark selected as resolved"

    def mark_as_unresolved(self, request, queryset):
        updated = queryset.update(is_resolved=False)
        self.message_user(request, f'{updated} inquiries marked as unresolved.')

    mark_as_unresolved.short_description = "Mark selected as unresolved"

    def send_response_email(self, request, queryset):
        """Send a response email to selected inquiries"""
        count = 0
        for inquiry in queryset:
            if inquiry.email:
                try:
                    send_mail(
                        subject=f"Re: {inquiry.subject}",
                        message=f"""
Dear {inquiry.name},

Thank you for contacting us regarding: {inquiry.subject}

We have received your inquiry and will get back to you shortly.

Best regards,
Hotel Team
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[inquiry.email],
                        fail_silently=False,
                    )
                    count += 1
                except Exception as e:
                    self.message_user(request, f"Failed to send email to {inquiry.email}: {str(e)}", level='ERROR')

        self.message_user(request, f'Response emails sent to {count} contacts.')

    send_response_email.short_description = "Send response email to selected"

    def export_inquiries_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_inquiries.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Name', 'Email', 'Phone', 'Inquiry Type', 'Subject',
            'Message', 'Resolved', 'Created Date'
        ])

        for inquiry in queryset:
            writer.writerow([
                inquiry.name,
                inquiry.email,
                inquiry.phone,
                inquiry.get_inquiry_type_display(),
                inquiry.subject,
                inquiry.message[:500],  # Limit message length
                'Yes' if inquiry.is_resolved else 'No',
                inquiry.created_at.strftime('%Y-%m-%d %H:%M')
            ])

        return response

    export_inquiries_csv.short_description = "Export selected to CSV"

    # Auto-save resolved notes when marking as resolved
    def save_model(self, request, obj, form, change):
        if obj.is_resolved and not obj.resolved_notes:
            obj.resolved_notes = f"Resolved by {request.user.username} on {obj.created_at.strftime('%Y-%m-%d')}"
        super().save_model(request, obj, form, change)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'is_active',  # Use actual field, not is_active_badge
        'subscribed_at',
        'days_subscribed'
    ]
    list_editable = ['is_active']  # Now matches list_display
    list_filter = [
        'is_active',
        'subscribed_at'
    ]
    search_fields = ['email']

    readonly_fields = ['subscribed_at']
    ordering = ['-subscribed_at']
    date_hierarchy = 'subscribed_at'

    fieldsets = (
        ('Subscriber Information', {
            'fields': (
                'email',
                'is_active'
            )
        }),
        ('Subscription Details', {
            'classes': ('collapse',),
            'fields': ('subscribed_at',)
        }),
    )

    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background-color: green; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">✓ ACTIVE</span>'
            )
        return format_html(
            '<span style="background-color: red; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">✗ INACTIVE</span>'
        )

    is_active_badge.short_description = 'Status'
    is_active_badge.admin_order_field = 'is_active'

    def days_subscribed(self, obj):
        from django.utils import timezone
        days = (timezone.now() - obj.subscribed_at).days
        return f"{days} days"

    days_subscribed.short_description = 'Days Subscribed'

    # Custom actions
    actions = [
        'activate_subscribers',
        'deactivate_subscribers',
        'export_subscribers_csv',
        'send_newsletter_test'
    ]

    def activate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscribers activated.')

    activate_subscribers.short_description = "Activate selected subscribers"

    def deactivate_subscribers(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscribers deactivated.')

    deactivate_subscribers.short_description = "Deactivate selected subscribers"

    def export_subscribers_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="newsletter_subscribers.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Email', 'Status', 'Subscribed Date', 'Days Subscribed'
        ])

        for subscriber in queryset:
            days = (timezone.now() - subscriber.subscribed_at).days
            writer.writerow([
                subscriber.email,
                'Active' if subscriber.is_active else 'Inactive',
                subscriber.subscribed_at.strftime('%Y-%m-%d'),
                days
            ])

        return response

    export_subscribers_csv.short_description = "Export subscribers to CSV"

    def send_newsletter_test(self, request, queryset):
        """Send test newsletter to selected subscribers"""
        count = 0
        for subscriber in queryset:
            if subscriber.is_active:
                try:
                    send_mail(
                        subject="Test Newsletter - Hotel Updates",
                        message="""
Hello!

This is a test newsletter from our hotel.

Thank you for subscribing to our updates.

Best regards,
Hotel Team
                        """,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[subscriber.email],
                        fail_silently=False,
                    )
                    count += 1
                except Exception as e:
                    self.message_user(request, f"Failed to send to {subscriber.email}: {str(e)}", level='ERROR')

        self.message_user(request, f'Test newsletters sent to {count} subscribers.')

    send_newsletter_test.short_description = "Send test newsletter to selected"


# Custom filters
from django.contrib.admin import SimpleListFilter


class ResolvedStatusFilter(SimpleListFilter):
    title = 'resolution status'
    parameter_name = 'resolution'

    def lookups(self, request, model_admin):
        return (
            ('resolved', 'Resolved'),
            ('unresolved', 'Unresolved'),
            ('recent_unresolved', 'Recent Unresolved (7 days)'),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta

        if self.value() == 'resolved':
            return queryset.filter(is_resolved=True)
        if self.value() == 'unresolved':
            return queryset.filter(is_resolved=False)
        if self.value() == 'recent_unresolved':
            week_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(is_resolved=False, created_at__gte=week_ago)


# Add custom filter to ContactInquiryAdmin
ContactInquiryAdmin.list_filter.append(ResolvedStatusFilter)


# Statistics display
class ContactStatsAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        # Add statistics to the context
        stats = {
            'total_inquiries': ContactInquiry.objects.count(),
            'unresolved_inquiries': ContactInquiry.objects.filter(is_resolved=False).count(),
            'total_subscribers': NewsletterSubscriber.objects.count(),
            'active_subscribers': NewsletterSubscriber.objects.filter(is_active=True).count(),
        }
        extra_context = extra_context or {}
        extra_context['stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)


# Apply stats to both admins
ContactInquiryAdmin.changelist_view = ContactStatsAdmin.changelist_view
NewsletterSubscriberAdmin.changelist_view = ContactStatsAdmin.changelist_view
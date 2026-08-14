from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'guest_name',
        'rating_stars',
        'title_preview',
        'country_flag',
        'stay_date',
        'is_approved_badge',
        'is_featured_badge',
        'created_at',
        'comment_preview'
    ]
    list_editable = []  # Remove list_editable since we're using methods for display
    list_filter = [
        'rating',
        'is_approved',
        'is_featured',
        'stay_date',
        'created_at',
        'guest_country'
    ]
    search_fields = [
        'guest_name',
        'title',
        'comment',
        'guest_country'
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'rating_display',
        'review_summary',
        'comment_display'
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Guest Information', {
            'fields': (
                'guest_name',
                'guest_country',
                'stay_date',
            )
        }),
        ('Review Content', {
            'fields': (
                'rating',
                'title',
                'comment',
            )
        }),
        ('Moderation', {
            'fields': (
                'is_approved',
                'is_featured',
            )
        }),
        ('Review Summary', {
            'classes': ('collapse',),
            'fields': ('review_summary',)
        }),
        ('Timestamps', {
            'classes': ('collapse',),
            'fields': (
                'created_at',
                'updated_at',
            )
        }),
    )

    def rating_stars(self, obj):
        # Check if rating exists and is not None
        if not obj or obj.rating is None:
            return format_html(
                '<div style="color: #999; font-style: italic;">No rating</div>'
            )

        stars = '⭐' * obj.rating
        empty_stars = '☆' * (5 - obj.rating)
        color = {
            1: '#ff6b6b',  # Red for 1 star
            2: '#ffa726',  # Orange for 2 stars
            3: '#ffd54f',  # Yellow for 3 stars
            4: '#a5d6a7',  # Light green for 4 stars
            5: '#4caf50',  # Green for 5 stars
        }.get(obj.rating, '#666')

        return format_html(
            '<div style="display: flex; align-items: center;">'
            '<span style="color: {}; font-size: 16px; margin-right: 8px;">{}{}</span>'
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 8px; font-size: 11px; font-weight: bold;">{}/5</span>'
            '</div>',
            color, stars, empty_stars, color, obj.rating
        )

    rating_stars.short_description = 'Rating'
    rating_stars.admin_order_field = 'rating'

    def rating_display(self, obj):
        # Check if object exists and has a rating
        if not obj or obj.rating is None:
            return format_html(
                '<div style="font-size: 16px; color: #999; margin: 10px 0; font-style: italic;">'
                'No rating selected'
                '</div>'
            )

        stars = '★' * obj.rating
        empty_stars = '☆' * (5 - obj.rating)
        return format_html(
            '<div style="font-size: 20px; color: #ffc107; margin: 10px 0;">'
            '{} {}'
            '<br><span style="font-size: 14px; color: #666;">({} out of 5 stars)</span>'
            '</div>',
            stars, empty_stars, obj.rating
        )

    rating_display.short_description = 'Rating Display'

    def country_flag(self, obj):
        if not obj:
            return "—"

        if obj.guest_country:
            # Simple flag emoji based on country name
            flag_emoji = "🏴" if obj.guest_country.lower() == 'ghana' else "🌍"
            return format_html(
                '<span title="{}">{} {}</span>',
                obj.guest_country, flag_emoji, obj.guest_country
            )
        return "—"

    country_flag.short_description = 'Country'
    country_flag.admin_order_field = 'guest_country'

    def is_approved_badge(self, obj):
        if not obj:
            return "—"

        if obj.is_approved:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">✓ APPROVED</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">⏳ PENDING</span>'
        )

    is_approved_badge.short_description = 'Approved'
    is_approved_badge.admin_order_field = 'is_approved'

    def is_featured_badge(self, obj):
        if not obj:
            return "—"

        if obj.is_featured:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">⭐ FEATURED</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">Standard</span>'
        )

    is_featured_badge.short_description = 'Featured'
    is_featured_badge.admin_order_field = 'is_featured'

    def title_preview(self, obj):
        if not obj or not obj.title:
            return "—"
        return Truncator(obj.title).chars(60)

    title_preview.short_description = 'Title'
    title_preview.admin_order_field = 'title'

    def comment_preview(self, obj):
        if not obj or not obj.comment:
            return "—"
        return Truncator(obj.comment).chars(80)

    comment_preview.short_description = 'Comment Preview'

    def comment_display(self, obj):
        if not obj or not obj.comment:
            return format_html(
                '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #6c757d; margin: 10px 0; color: #999; font-style: italic;">'
                'No comment provided'
                '</div>'
            )

        return format_html(
            '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff; margin: 10px 0;">'
            '<strong>Comment Preview:</strong><br>'
            '<div style="margin-top: 8px; color: #555; line-height: 1.5; font-style: italic;">{}</div>'
            '</div>',
            obj.comment.replace('\n', '<br>')
        )

    comment_display.short_description = ''

    def review_summary(self, obj):
        if not obj:
            return format_html(
                '<div style="background: #f8f9fa; color: #666; padding: 15px; border-radius: 8px; margin: 10px 0; font-style: italic;">'
                'No review data available'
                '</div>'
            )

        # Calculate days between stay and review
        if obj.stay_date and obj.created_at:
            days_ago = (obj.created_at.date() - obj.stay_date).days
            days_text = f"{days_ago} days after stay"
        else:
            days_text = 'Not specified'

        return format_html(
            '<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 8px; margin: 10px 0;">'
            '<h4 style="margin: 0 0 10px 0; color: white;">📊 Review Summary</h4>'
            '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 13px;">'
            '<div><strong>Guest:</strong> {}</div>'
            '<div><strong>Country:</strong> {}</div>'
            '<div><strong>Stay Date:</strong> {}</div>'
            '<div><strong>Reviewed:</strong> {}</div>'
            '<div><strong>Rating:</strong> {}/5 stars</div>'
            '<div><strong>Status:</strong> {}</div>'
            '</div>'
            '</div>',
            obj.guest_name or 'Not specified',
            obj.guest_country or 'Not specified',
            obj.stay_date.strftime('%b %d, %Y') if obj.stay_date else 'Not specified',
            days_text,
            obj.rating if obj.rating else 'Not rated',
            'Approved' if obj.is_approved else 'Pending'
        )

    review_summary.short_description = ''

    # Custom actions
    actions = [
        'approve_reviews',
        'unapprove_reviews',
        'feature_reviews',
        'unfeature_reviews',
        'export_reviews_csv',
        'generate_rating_report'
    ]

    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} reviews approved and published.')

    approve_reviews.short_description = "Approve selected reviews"

    def unapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} reviews unapproved and hidden.')

    unapprove_reviews.short_description = "Unapprove selected reviews"

    def feature_reviews(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} reviews marked as featured.')

    feature_reviews.short_description = "Mark selected as featured"

    def unfeature_reviews(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} reviews unfeatured.')

    unfeature_reviews.short_description = "Remove featured status"

    def export_reviews_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reviews_export.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Guest Name', 'Country', 'Rating', 'Title', 'Comment',
            'Stay Date', 'Approved', 'Featured', 'Created Date'
        ])

        for review in queryset:
            writer.writerow([
                review.guest_name,
                review.guest_country or '',
                review.rating or '',
                review.title,
                review.comment[:500] if review.comment else '',  # Limit comment length
                review.stay_date.strftime('%Y-%m-%d') if review.stay_date else '',
                'Yes' if review.is_approved else 'No',
                'Yes' if review.is_featured else 'No',
                review.created_at.strftime('%Y-%m-%d %H:%M') if review.created_at else ''
            ])

        return response

    export_reviews_csv.short_description = "Export reviews to CSV"

    def generate_rating_report(self, request, queryset):
        """Generate a rating analysis report"""
        from collections import Counter

        ratings = Counter()
        approved_count = 0
        featured_count = 0

        for review in queryset:
            if review.rating:
                ratings[review.rating] += 1
            if review.is_approved:
                approved_count += 1
            if review.is_featured:
                featured_count += 1

        total = queryset.count()
        if total > 0:
            # Only include reviews with ratings in average calculation
            rated_reviews = [r.rating for r in queryset if r.rating]
            if rated_reviews:
                avg_rating = sum(rated_reviews) / len(rated_reviews)
            else:
                avg_rating = 0
        else:
            avg_rating = 0

        report = f"📈 Review Rating Report\n\n"
        report += f"Total Reviews: {total}\n"
        report += f"Average Rating: {avg_rating:.1f}/5\n"
        report += f"Approved: {approved_count} ({approved_count / total * 100:.1f}%)\n" if total > 0 else "Approved: 0 (0%)\n"
        report += f"Featured: {featured_count} ({featured_count / total * 100:.1f}%)\n\n" if total > 0 else "Featured: 0 (0%)\n\n"
        report += "Rating Distribution:\n"

        for rating in range(5, 0, -1):
            count = ratings.get(rating, 0)
            percentage = (count / total * 100) if total > 0 else 0
            stars = '★' * rating + '☆' * (5 - rating)
            report += f"{stars} {rating} stars: {count} ({percentage:.1f}%)\n"

        self.message_user(request, format_html(
            '<pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace;">{}</pre>',
            report))

    generate_rating_report.short_description = "Generate rating report"

    def changelist_view(self, request, extra_context=None):
        from django.db.models import Avg, Count

        stats = {
            'total_reviews': Review.objects.count(),
            'approved_reviews': Review.objects.filter(is_approved=True).count(),
            'featured_reviews': Review.objects.filter(is_featured=True).count(),
            'average_rating': Review.objects.filter(is_approved=True, rating__isnull=False).aggregate(
                avg=Avg('rating')
            )['avg'] or 0,
            'rating_distribution': Review.objects.filter(is_approved=True, rating__isnull=False).values(
                'rating'
            ).annotate(count=Count('id')).order_by('-rating')
        }

        extra_context = extra_context or {}
        extra_context['stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)


# Custom filters
from django.contrib.admin import SimpleListFilter


class RatingFilter(SimpleListFilter):
    title = 'rating'
    parameter_name = 'rating_range'

    def lookups(self, request, model_admin):
        return (
            ('5_star', '5 Stars (Excellent)'),
            ('4_star', '4 Stars (Very Good)'),
            ('3_star', '3 Stars (Good)'),
            ('1_2_star', '1-2 Stars (Needs Improvement)'),
            ('no_rating', 'No Rating'),
        )

    def queryset(self, request, queryset):
        if self.value() == '5_star':
            return queryset.filter(rating=5)
        elif self.value() == '4_star':
            return queryset.filter(rating=4)
        elif self.value() == '3_star':
            return queryset.filter(rating=3)
        elif self.value() == '1_2_star':
            return queryset.filter(rating__in=[1, 2])
        elif self.value() == 'no_rating':
            return queryset.filter(rating__isnull=True)


class ApprovalStatusFilter(SimpleListFilter):
    title = 'approval status'
    parameter_name = 'approval'

    def lookups(self, request, model_admin):
        return (
            ('approved', 'Approved Only'),
            ('pending', 'Pending Approval'),
            ('approved_featured', 'Approved & Featured'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'approved':
            return queryset.filter(is_approved=True)
        elif self.value() == 'pending':
            return queryset.filter(is_approved=False)
        elif self.value() == 'approved_featured':
            return queryset.filter(is_approved=True, is_featured=True)


# Add custom filters to the ReviewAdmin
ReviewAdmin.list_filter.extend([RatingFilter, ApprovalStatusFilter])
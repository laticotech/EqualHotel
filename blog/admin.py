from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from .models import BlogCategory, BlogPost


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug',
        'post_count',
        'description_preview'
    ]
    list_display_links = ['name', 'slug']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Category Information', {
            'fields': (
                'name',
                'slug',
                'description'
            )
        }),
    )
    ordering = ['name']

    def description_preview(self, obj):
        return Truncator(obj.description).chars(100)

    description_preview.short_description = 'Description Preview'

    def post_count(self, obj):
        return obj.blogpost_set.count()

    post_count.short_description = 'Posts'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'author',
        'is_published',
        'published_date',
        'created_at',
        'featured_image_tag',
        'status'
    ]
    list_filter = [
        'is_published',
        'category',
        'author',
        'published_date',
        'created_at'
    ]
    search_fields = [
        'title',
        'content',
        'excerpt',
        'author',
        'tags'
    ]
    list_editable = ['is_published']
    list_select_related = ['category']
    readonly_fields = [
        'created_at',
        'updated_at',
        'featured_image_tag',
        'content_preview',
        'excerpt_preview'
    ]
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    ordering = ['-published_date']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title',
                'slug',
                'featured_image',
                'featured_image_tag'
            )
        }),
        ('Content', {
            'fields': (
                'excerpt',
                'excerpt_preview',
                'content',
                'content_preview'
            )
        }),
        ('Categorization', {
            'fields': (
                'category',
                'tags',
                'author'
            )
        }),
        ('Publishing', {
            'fields': (
                'is_published',
                'published_date'
            )
        }),
        ('SEO Settings', {
            'classes': ('collapse',),
            'fields': (
                'meta_title',
                'meta_description'
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

    def featured_image_tag(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" width="60" height="40" style="object-fit: cover; border-radius: 4px;" />',
                obj.featured_image.url
            )
        return "No Image"

    featured_image_tag.short_description = 'Image'

    def content_preview(self, obj):
        return Truncator(obj.content).chars(200)

    content_preview.short_description = 'Content Preview'

    def excerpt_preview(self, obj):
        return Truncator(obj.excerpt).chars(100)

    excerpt_preview.short_description = 'Excerpt Preview'

    def status(self, obj):
        if obj.is_published:
            if obj.published_date:
                return format_html(
                    '<span style="color: green; font-weight: bold;">✓ Published</span>'
                )
            return format_html(
                '<span style="color: orange; font-weight: bold;">⚠ Published (no date)</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Draft</span>'
        )

    status.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')

    # Custom actions
    actions = ['publish_posts', 'unpublish_posts']

    def publish_posts(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f'{updated} posts were successfully published.')

    publish_posts.short_description = "Publish selected posts"

    def unpublish_posts(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} posts were successfully unpublished.')

    unpublish_posts.short_description = "Unpublish selected posts"

    # Auto-set published_date when publishing
    def save_model(self, request, obj, form, change):
        if obj.is_published and not obj.published_date:
            from django.utils import timezone
            obj.published_date = timezone.now()
        super().save_model(request, obj, form, change)


# Optional: Custom filters for better organization
from django.contrib.admin import SimpleListFilter


class HasPublishedDateFilter(SimpleListFilter):
    title = 'published date status'
    parameter_name = 'has_published_date'

    def lookups(self, request, model_admin):
        return (
            ('has_date', 'Has published date'),
            ('no_date', 'No published date'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'has_date':
            return queryset.exclude(published_date__isnull=True)
        if self.value() == 'no_date':
            return queryset.filter(published_date__isnull=True)


# Add the custom filter to BlogPostAdmin
BlogPostAdmin.list_filter.append(HasPublishedDateFilter)


# Optional: Inline editing for related models
class BlogPostInline(admin.StackedInline):
    model = BlogPost
    extra = 0
    fields = ['title', 'is_published', 'published_date']
    readonly_fields = ['published_date']
    show_change_link = True


# Update BlogCategoryAdmin to show posts inline
BlogCategoryAdmin.inlines = [BlogPostInline]


# Optional: Custom admin site enhancements
class BlogAdminSite(admin.AdminSite):
    site_header = "Blog Management"
    site_title = "Blog Admin"
    index_title = "Blog Content Management"


# Optional: Add export functionality
from django.http import HttpResponse
import csv


def export_blog_posts(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="blog_posts.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Category', 'Author', 'Published', 'Published Date', 'Created'])

    for post in queryset:
        writer.writerow([
            post.title,
            post.category.name if post.category else 'No Category',
            post.author,
            'Yes' if post.is_published else 'No',
            post.published_date,
            post.created_at
        ])

    return response


export_blog_posts.short_description = "Export selected posts to CSV"

# Add export action to BlogPostAdmin
BlogPostAdmin.actions.append(export_blog_posts)
# blog/models.py
from django.db import models


class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Blog categories"

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    featured_image = models.ImageField(upload_to='blog/')

    # Categorization
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")

    # Publishing
    author = models.CharField(max_length=100, default="Hotel Staff")
    is_published = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True, blank=True)

    # SEO
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date']

    def __str__(self):
        return self.title
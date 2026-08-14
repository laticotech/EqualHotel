from django import forms
from .models import BlogPost, BlogCategory


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = [
            'title', 'slug', 'content', 'excerpt', 'featured_image',
            'category', 'tags', 'author', 'is_published', 'published_date',
            'meta_title', 'meta_description'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'meta_description': forms.Textarea(attrs={'rows': 3}),
            'published_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
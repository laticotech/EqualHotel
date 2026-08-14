from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['guest_name', 'guest_country', 'rating', 'title', 'comment', 'stay_date']
        widgets = {
            'guest_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name'
            }),
            'guest_country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Country (Optional)'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review Title'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience...',
                'rows': 5
            }),
            'stay_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating not in [1, 2, 3, 4, 5]:
            raise forms.ValidationError('Please select a valid rating.')
        return rating
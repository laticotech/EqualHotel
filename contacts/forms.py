from django import forms
from .models import ContactInquiry, NewsletterSubscriber


class ContactInquiryForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'inquiry_type', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email Address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Phone Number (Optional)'
            }),
            'inquiry_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject of Your Message'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your Message...',
                'rows': 5
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.replace(' ', '').replace('-', '').replace('+', '').isdigit():
            raise forms.ValidationError('Please enter a valid phone number.')
        return phone


class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            })
        }
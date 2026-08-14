from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'bio', 'profile_pic']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# forms.py
from bookings.models import BookingPayment
from services.models import ServiceReservationPayment


class BookingPaymentForm(forms.ModelForm):
    class Meta:
        model = BookingPayment
        fields = ['payment_method', 'amount_paid', 'payment_status', 'transaction_id', 'payment_notes']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ServiceReservationPaymentForm(forms.ModelForm):
    class Meta:
        model = ServiceReservationPayment
        fields = ['payment_method', 'amount_paid', 'payment_status', 'transaction_id', 'payment_notes']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_status': forms.Select(attrs={'class': 'form-select'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
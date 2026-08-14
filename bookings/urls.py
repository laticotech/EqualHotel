from django.urls import path
from . import views

urlpatterns = [
    path('check-availability/', views.check_availability, name='check_availability'),
    path('create-booking/', views.create_booking, name='create_booking'),
    path('booking-success/<str:booking_reference>/', views.booking_success, name='booking_success'),

    path('send-email-confirmation/<str:booking_reference>/', views.resend_confirmation_email, name='resend_confirmation_email'),

    path('test-email/', views.test_email, name='test_email'),  # Add this line
]
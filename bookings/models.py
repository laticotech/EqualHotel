# bookings/models.py
from django.db import models
import random
import string


class Booking(models.Model):
    BOOKING_STATUS = (
        ('pending', 'Pending Payment'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )

    # Booking details
    booking_reference = models.CharField(max_length=12, unique=True)
    room = models.ForeignKey('rooms.Room', on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    adults = models.PositiveIntegerField(default=1)
    children = models.PositiveIntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Guest information
    guest_name = models.CharField(max_length=200)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)
    guest_address = models.TextField(blank=True)
    special_requests = models.TextField(blank=True)

    # Status
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking {self.booking_reference}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        super().save(*args, **kwargs)

    def generate_booking_reference(self):
        return 'BK' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    @property
    def nights(self):
        return (self.check_out - self.check_in).days


class BookingPayment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    PAYMENT_METHODS = (
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
    )

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payment for {self.booking.booking_reference}"
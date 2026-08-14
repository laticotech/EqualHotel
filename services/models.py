# services/models.py
from django.db import models
import random
import string
from django.utils import timezone


class Service(models.Model):
    SERVICE_CATEGORIES = (
        ('dining', 'Dining'),
        ('spa', 'Spa & Wellness'),
        ('business', 'Business'),
        ('recreation', 'Recreation'),
        ('transport', 'Transportation'),
        ('other', 'Other Services'),
    )

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=SERVICE_CATEGORIES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_free = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to='services/', blank=True)

    # Availability
    available_days = models.CharField(max_length=100, blank=True)  # "Mon-Fri", "Daily"
    available_times = models.CharField(max_length=100, blank=True)  # "9:00-18:00"
    requires_booking = models.BooleanField(default=False)

    # Display
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class ServiceReservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='reservations')
    guest_name = models.CharField(max_length=200)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)

    # Reservation details
    reservation_date = models.DateField()
    reservation_time = models.TimeField()
    number_of_guests = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)

    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reservation_number = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-reservation_date', '-reservation_time']

    def __str__(self):
        return f"{self.reservation_number} - {self.guest_name}"

    def save(self, *args, **kwargs):
        if not self.reservation_number:
            self.reservation_number = self.generate_reservation_number()
        super().save(*args, **kwargs)

    def generate_reservation_number(self):
        return f"SRV{random.randint(1000, 9999)}{string.ascii_uppercase[random.randint(0, 25)]}"

    # Payment handling properties
    @property
    def total_amount(self):
        """Calculate total amount for the service reservation"""
        if self.service.is_free:
            return 0
        if self.service.price:
            return self.service.price * self.number_of_guests
        return 0

    @property
    def requires_payment(self):
        """Check if this reservation requires payment"""
        return not self.service.is_free and self.total_amount > 0

    @property
    def payment_status(self):
        """Get payment status from related payment object"""
        if hasattr(self, 'payment'):
            return self.payment.payment_status
        return 'no_payment_required' if not self.requires_payment else 'pending'

    @property
    def is_paid(self):
        """Check if reservation is fully paid"""
        if hasattr(self, 'payment'):
            return self.payment.is_fully_paid
        return not self.requires_payment  # If no payment required, consider it paid

    def create_payment_record(self):
        """Create a payment record if needed"""
        if self.requires_payment and not hasattr(self, 'payment'):
            return ServiceReservationPayment.objects.create(
                service_reservation=self,
                amount_expected=self.total_amount
            )
        return None

    @property
    def can_be_confirmed(self):
        """Check if reservation can be confirmed (paid or no payment required)"""
        return self.is_paid or not self.requires_payment


class ServiceReservationPayment(models.Model):
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

    # Relationship with service reservation
    service_reservation = models.OneToOneField(
        ServiceReservation,
        on_delete=models.CASCADE,
        related_name='payment'
    )

    # Payment details - consistent with BookingPayment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='paystack')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    # Keep only essential additional fields
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-payment_date']  # Changed from '-created_at' to '-payment_date'
        verbose_name = 'Service Reservation Payment'
        verbose_name_plural = 'Service Reservation Payments'

    def __str__(self):
        return f"Payment for {self.service_reservation.reservation_number}"

    def save(self, *args, **kwargs):
        if not self.payment_reference:
            self.payment_reference = self.generate_payment_reference()
        super().save(*args, **kwargs)

    def generate_payment_reference(self):
        return f"SRV{random.randint(10000, 99999)}{string.ascii_uppercase[random.randint(0, 25)]}"

    @property
    def is_fully_paid(self):
        """Check if payment is fully completed"""
        return self.payment_status == 'completed'

    @property
    def amount_expected(self):
        """Get expected amount from service reservation"""
        return self.service_reservation.total_amount

    @property
    def balance_due(self):
        """Calculate balance due"""
        if self.is_fully_paid:
            return 0
        return self.service_reservation.total_amount - self.amount_paid

    def mark_as_paid(self, amount=None, method=None, transaction_id=None):
        """Helper method to mark payment as completed"""
        if amount:
            self.amount_paid = amount
        else:
            self.amount_paid = self.service_reservation.total_amount

        if method:
            self.payment_method = method
        if transaction_id:
            self.transaction_id = transaction_id

        self.payment_status = 'completed'
        self.save()

        # Auto-confirm the reservation if it was pending
        if self.service_reservation.status == 'pending':
            self.service_reservation.status = 'confirmed'
            self.service_reservation.save()
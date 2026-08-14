from django.utils import timezone
from bookings.models import Booking, BookingPayment
from services.models import ServiceReservation, ServiceReservationPayment
from contacts.models import ContactInquiry


# context_processors.py
def notification_counts(request):
    if request.user.is_authenticated:
        # Get the last viewed timestamp from session
        last_viewed = request.session.get('notifications_last_viewed')

        if last_viewed:
            try:
                last_viewed_time = timezone.datetime.fromisoformat(last_viewed)
                # Only count items created AFTER the user last viewed notifications
                count_pending_bookings = Booking.objects.filter(
                    guest_email=request.user.email,
                    status__in=['pending', 'confirmed'],
                    created_at__gt=last_viewed_time
                ).count()

                count_pending_reservations = ServiceReservation.objects.filter(
                    guest_email=request.user.email,
                    status__in=['pending', 'confirmed'],
                    created_at__gt=last_viewed_time
                ).count()
            except (ValueError, AttributeError):
                # If there's an error parsing the timestamp, count all
                count_pending_bookings = Booking.objects.filter(
                    guest_email=request.user.email,
                    status__in=['pending', 'confirmed']
                ).count()

                count_pending_reservations = ServiceReservation.objects.filter(
                    guest_email=request.user.email,
                    status__in=['pending', 'confirmed']
                ).count()
        else:
            # If never viewed, count all pending items
            count_pending_bookings = Booking.objects.filter(
                guest_email=request.user.email,
                status__in=['pending', 'confirmed']
            ).count()

            count_pending_reservations = ServiceReservation.objects.filter(
                guest_email=request.user.email,
                status__in=['pending', 'confirmed']
            ).count()

        return {
            'count_pending_bookings': count_pending_bookings,
            'count_pending_reservations': count_pending_reservations,
            'total_pending_count': count_pending_bookings + count_pending_reservations,
        }

    return {
        'count_pending_bookings': 0,
        'count_pending_reservations': 0,
        'total_pending_count': 0,
    }


def admin_notifications(request):
    """Context processor for admin notification counts"""
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        # Count pending items for admin notifications
        pending_bookings_count = Booking.objects.filter(status='pending').count()
        pending_reservations_count = ServiceReservation.objects.filter(status='pending').count()
        unread_messages_count = ContactInquiry.objects.filter(is_resolved=False).count()
        pending_booking_payments = BookingPayment.objects.filter(payment_status='pending').count()
        pending_service_payments = ServiceReservationPayment.objects.filter(payment_status='pending').count()

        total_admin_notifications = (
                pending_bookings_count +
                pending_reservations_count +
                unread_messages_count +
                pending_booking_payments +
                pending_service_payments
        )

        return {
            'pending_bookings_count': pending_bookings_count,
            'pending_reservations_count': pending_reservations_count,
            'unread_messages_count': unread_messages_count,
            'pending_booking_payments_count': pending_booking_payments,
            'pending_service_payments_count': pending_service_payments,
            'total_admin_notifications': total_admin_notifications,
        }

    return {}
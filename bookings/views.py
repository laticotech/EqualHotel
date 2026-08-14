from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Booking, BookingPayment
from rooms.models import RoomType, Room
from django.contrib import messages
import json

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# Add this to your bookings/views.py
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from accounts.models import User, Profile
from hotel.models import Hotel


def check_availability(request):
    if request.method == 'GET':
        check_in = request.GET.get('check_in')
        check_out = request.GET.get('check_out')
        adults = int(request.GET.get('adults', 2))
        children = int(request.GET.get('children', 0))

        total_guests = adults + children

        # Convert string dates to datetime objects
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        # Validate dates
        if check_in_date >= check_out_date:
            return JsonResponse({'error': 'Check-out date must be after check-in date'}, status=400)

        if check_in_date < timezone.now().date():
            return JsonResponse({'error': 'Check-in date cannot be in the past'}, status=400)

        # Find available room types that can accommodate the guests
        available_room_types = RoomType.objects.filter(
            is_available=True,
            capacity__gte=total_guests
        ).prefetch_related('rooms', 'images')

        available_rooms_data = []

        for room_type in available_room_types:
            # Find available rooms of this type that are not booked for the selected dates
            booked_rooms = Booking.objects.filter(
                room__room_type=room_type,
                check_out__gt=check_in_date,
                check_in__lt=check_out_date,
                status__in=['confirmed', 'checked_in', 'pending']
            ).values_list('room_id', flat=True)

            available_rooms = room_type.rooms.filter(
                is_available=True
            ).exclude(id__in=booked_rooms)

            if available_rooms.exists():
                nights = (check_out_date - check_in_date).days
                total_price = room_type.base_price * nights

                room_data = {
                    'id': room_type.id,
                    'name': room_type.name,
                    'slug': room_type.slug,
                    'base_price': float(room_type.base_price),
                    'total_price': float(total_price),
                    'nights': nights,
                    'capacity': room_type.capacity,
                    'size': room_type.size,
                    'bed_type': room_type.bed_type,
                    'description': room_type.description,
                    'available_count': available_rooms.count(),
                    'featured_image': room_type.featured_image.url if room_type.featured_image else None,
                    'amenities': list(room_type.amenities.values('name', 'icon'))
                }
                available_rooms_data.append(room_data)

        return JsonResponse({
            'check_in': check_in,
            'check_out': check_out,
            'adults': adults,
            'children': children,
            'total_guests': total_guests,
            'available_rooms': available_rooms_data
        })

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_booking(request):
    if request.method == 'POST':
        try:
            print("Received booking request")  # Debug
            data = json.loads(request.body)
            print("Parsed data:", data)  # Debug

            room_type_id = data.get('room_type_id')
            check_in = data.get('check_in')
            check_out = data.get('check_out')
            adults = data.get('adults', 2)
            children = data.get('children', 0)
            guest_name = data.get('guest_name')
            guest_email = data.get('guest_email')
            guest_phone = data.get('guest_phone')
            guest_address = data.get('guest_address', '')
            special_requests = data.get('special_requests', '')

            # Debug: Print all received data
            print(f"Room Type ID: {room_type_id}")
            print(f"Check-in: {check_in}")
            print(f"Check-out: {check_out}")
            print(f"Adults: {adults}")
            print(f"Children: {children}")
            print(f"Guest Name: {guest_name}")
            print(f"Guest Email: {guest_email}")
            print(f"Guest Phone: {guest_phone}")

            # Validate required fields with specific error messages
            missing_fields = []
            if not room_type_id:
                missing_fields.append('room_type_id')
            if not check_in:
                missing_fields.append('check_in')
            if not check_out:
                missing_fields.append('check_out')
            if not guest_name:
                missing_fields.append('guest_name')
            if not guest_email:
                missing_fields.append('guest_email')
            if not guest_phone:
                missing_fields.append('guest_phone')

            if missing_fields:
                error_msg = f'Missing required fields: {", ".join(missing_fields)}'
                print(f"Validation error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

            # Convert dates
            try:
                check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
                check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
                print(f"Parsed dates - Check-in: {check_in_date}, Check-out: {check_out_date}")
            except (ValueError, TypeError) as e:
                error_msg = f'Invalid date format: {str(e)}'
                print(f"Date parsing error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

            nights = (check_out_date - check_in_date).days
            print(f"Calculated nights: {nights}")

            # Validate dates
            if check_in_date >= check_out_date:
                error_msg = 'Check-out date must be after check-in date'
                print(f"Date validation error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

            if check_in_date < timezone.now().date():
                error_msg = 'Check-in date cannot be in the past'
                print(f"Date validation error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

            # Get room type
            try:
                room_type = RoomType.objects.get(id=room_type_id)
                print(f"Found room type: {room_type.name}")
            except RoomType.DoesNotExist:
                error_msg = 'Room type not found'
                print(f"Room type error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

            # Check if room type is available
            if not room_type.is_available:
                error_msg = 'This room type is not available'
                print(f"Availability error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

            # Check guest capacity
            total_guests = int(adults) + int(children)
            if total_guests > room_type.capacity:
                error_msg = f'This room type can only accommodate {room_type.capacity} guests'
                print(f"Capacity error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

            # Find available room
            booked_rooms = Booking.objects.filter(
                room__room_type=room_type,
                check_out__gt=check_in_date,
                check_in__lt=check_out_date,
                status__in=['confirmed', 'checked_in', 'pending']
            ).values_list('room_id', flat=True)

            available_room = room_type.rooms.filter(
                is_available=True
            ).exclude(id__in=booked_rooms).first()

            if not available_room:
                error_msg = 'No rooms available for selected dates'
                print(f"Room availability error: {error_msg}")
                return JsonResponse({'error': error_msg}, status=400)

            # Calculate total price
            total_price = room_type.base_price * nights
            print(f"Calculated total price: {total_price}")

            # Create booking
            booking = Booking(
                room=available_room,
                check_in=check_in_date,
                check_out=check_out_date,
                adults=int(adults),
                children=int(children),
                total_price=total_price,
                guest_name=guest_name,
                guest_email=guest_email,
                guest_phone=guest_phone,
                guest_address=guest_address,
                special_requests=special_requests,
                status='pending'
            )
            booking.save()
            print(f"Booking created successfully: {booking.booking_reference}")

            # Send confirmation email with error handling
            email_sent = False
            email_error = None
            try:
                email_sent = send_booking_confirmation_email(booking)
                print(f"Email sent: {email_sent}")
            except Exception as e:
                email_error = str(e)
                print(f"Email error: {email_error}")

            response_data = {
                'success': True,
                'booking_reference': booking.booking_reference,
                'total_price': float(total_price),
                'nights': nights,
                'email_sent': email_sent,
                'email_error': email_error,
                'message': 'Booking created successfully!' + (' Confirmation email sent.' if email_sent else ' Email failed but booking is confirmed.')
            }

            print(f"Sending success response: {response_data}")
            return JsonResponse(response_data)

        except json.JSONDecodeError as e:
            error_msg = f'Invalid JSON data: {str(e)}'
            print(f"JSON error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)
        except Exception as e:
            error_msg = f'Server error: {str(e)}'
            print(f"General error: {error_msg}")
            return JsonResponse({'error': error_msg}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required()
def booking_success(request, booking_reference):
    booking = get_object_or_404(Booking, booking_reference=booking_reference)
    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    room = 'room'

    context = {
        'booking': booking,
        'hotel': hotel,
        'profile': profile,
        'room': room,
    }
    return render(request, 'booking_success.html', context)


@login_required()
def send_booking_confirmation_email(booking):
    """Send booking confirmation email to guest - FIXED VERSION"""
    try:
        subject = f'Booking Confirmation - {booking.booking_reference}'
        hotel = Hotel.objects.get(pk=1)

        # Create HTML email content
        context = {
            'hotel': hotel,
            'booking': booking,
            'hotel_name': hotel.name,  # Use actual hotel name
            'contact_email': 'laticotechgh@gmail.com',
            'contact_phone': hotel.phone if hotel.phone else '+233 XXX XXX XXX',
        }

        # Don't include profile in email context since we don't have request
        # The email template should work with just booking and hotel data

        html_message = render_to_string('booking_confirmation.html', context)
        plain_message = strip_tags(html_message)

        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email='laticotechgh@gmail.com',  # Or use DEFAULT_FROM_EMAIL from settings
            recipient_list=[booking.guest_email],
            html_message=html_message,
            fail_silently=False,
        )

        print(f"Email sent to {booking.guest_email}. Result: {result}")
        return True

    except Exception as e:
        print(f"Failed to send email to {booking.guest_email}: {str(e)}")
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Email sending failed: {str(e)}")
        return False


@login_required()
@csrf_exempt
def resend_confirmation_email(request, booking_reference):
    if request.method == 'POST':
        try:
            booking = Booking.objects.get(booking_reference=booking_reference)
            send_booking_confirmation_email(booking)
            return JsonResponse({'success': True, 'message': 'Confirmation email sent successfully'})
        except Booking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def test_email(request):
    """Test email functionality - for debugging"""
    try:
        # Create a test booking object
        from rooms.models import RoomType, Room

        # Get any room type and room for testing
        room_type = RoomType.objects.first()
        if not room_type:
            return JsonResponse({'error': 'No room types available for testing'}, status=400)

        room = room_type.rooms.first()
        if not room:
            return JsonResponse({'error': 'No rooms available for testing'}, status=400)

        # Create a mock booking object for testing
        class MockBooking:
            def __init__(self):
                self.booking_reference = 'TEST123'
                self.guest_name = 'Test User'
                self.guest_email = 'laticotechgh@gmail.com'  # Send to yourself for testing
                self.guest_phone = '+233000000000'
                self.check_in = timezone.now().date()
                self.check_out = timezone.now().date()
                self.adults = 2
                self.children = 0
                self.total_price = 100.00
                self.nights = 1
                self.room = room
                self.special_requests = 'Test booking'

        test_booking = MockBooking()

        # Test email sending
        email_sent = send_booking_confirmation_email(test_booking)

        if email_sent:
            return JsonResponse({
                'status': 'Email sent successfully',
                'to': test_booking.guest_email,
                'message': 'Check your email inbox (and spam folder)'
            })
        else:
            return JsonResponse({
                'status': 'Email failed',
                'message': 'Check your email configuration and logs'
            })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
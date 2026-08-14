from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Service, ServiceReservation
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.html import strip_tags
from hotel.models import Hotel
from accounts.models import Profile, User


def service_list(request):
    """Display all active services grouped by category"""
    services = Service.objects.filter(is_active=True).order_by('category', 'display_order', 'name')
    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None

    # Group services by category
    services_by_category = {}
    for service in services:
        category_name = service.get_category_display()
        if category_name not in services_by_category:
            services_by_category[category_name] = []
        services_by_category[category_name].append(service)
    served = 'served'
    context = {
        'services_by_category': services_by_category,
        'services': services,
        'served': served,
        'hotel': hotel,
        'profile': profile,
    }
    return render(request, 'service_list.html', context)


def service_detail(request, service_id):
    """Display detailed information about a specific service"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None

    related_services = Service.objects.filter(
        category=service.category,
        is_active=True
    ).exclude(id=service.id).order_by('display_order')[:4]
    served = 'served'
    context = {
        'hotel': hotel,
        'profile': profile,
        'service': service,
        'served': served,
        'related_services': related_services,
    }
    return render(request, 'service_detail.html', context)


@login_required
def service_reservation(request, service_id):
    """Handle service reservation form - requires login"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    hotel = Hotel.objects.get(pk=1)

    # Get user profile - user is authenticated due to @login_required
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None

    if request.method == 'POST':
        # Process reservation form
        guest_name = request.POST.get('guest_name')
        guest_email = request.POST.get('guest_email')
        guest_phone = request.POST.get('guest_phone')
        reservation_date = request.POST.get('reservation_date')
        reservation_time = request.POST.get('reservation_time')
        number_of_guests = request.POST.get('number_of_guests', 1)
        special_requests = request.POST.get('special_requests', '')

        # Basic validation
        if not all([guest_name, guest_email, guest_phone, reservation_date, reservation_time]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'service_reservation.html', {
                'service': service,
                'hotel': hotel,
                'profile': profile,
                'served': 'served'
            })

        try:
            # Create reservation
            reservation = ServiceReservation(
                service=service,
                guest_name=guest_name,
                guest_email=guest_email,
                guest_phone=guest_phone,
                reservation_date=reservation_date,
                reservation_time=reservation_time,
                number_of_guests=number_of_guests,
                special_requests=special_requests
            )
            reservation.save()

            # Send confirmation email
            send_service_reservation_email(reservation)

            messages.success(request, 'Your reservation has been submitted successfully!')
            return redirect('service_reservation_success', reservation_id=reservation.id)

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    served = 'served'
    context = {
        'service': service,
        'served': served,
        'hotel': hotel,
        'profile': profile,
    }
    return render(request, 'service_reservation.html', context)


@login_required
def service_reservation_success(request, reservation_id):
    """Display reservation success page"""
    reservation = get_object_or_404(ServiceReservation, id=reservation_id)
    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    served = 'served'
    context = {
        'reservation': reservation,
        'served': served,
        'hotel': hotel,
        'profile': profile,
    }
    return render(request, 'reservation_success.html', context)


@login_required()
def send_service_reservation_email(reservation):
    """Send reservation confirmation email - FIXED: removed request dependency"""
    try:
        subject = f'Service Reservation Confirmation - {reservation.reservation_number}'

        try:
            hotel = Hotel.objects.get(pk=1)
            hotel_name = hotel.name
        except Hotel.DoesNotExist:
            hotel_name = "Our Hotel"

        context = {
            'hotel_name': hotel_name,
            'reservation': reservation,
            'service': reservation.service,
            'contact_email': 'laticotechgh@gmail.com',
            'contact_phone': '+233 XXX XXX XXX',
        }

        html_message = render_to_string('emails/reservation_confirmation.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email='laticotechgh@gmail.com',
            recipient_list=[reservation.guest_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.utils.timesince import timesince as timesince_filter
from django.utils.timesince import timesince
from django.contrib.auth.decorators import login_required, user_passes_test  # Add this import

from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, ProfileUpdateForm, UserUpdateForm, ServiceReservationPaymentForm, BookingPaymentForm

from .models import Profile
from hotel.models import Hotel, TeamMember, Event
from bookings.models import Booking, BookingPayment
from services.models import ServiceReservation, ServiceReservationPayment
from contacts.models import ContactInquiry, NewsletterSubscriber
from blog.models import BlogCategory, BlogPost
from reviews.models import Review

from django.contrib.admin.views.decorators import staff_member_required
from datetime import timedelta
from django.db.models import Sum, Count, Q
from django.core.paginator import Paginator
from django.http import JsonResponse

from blog.forms import BlogPostForm
from hotel.forms import TeamMemberForm, EventForm


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Create profile for the user
            Profile.objects.create(
                user=user,
                phone=request.POST.get('phone', ''),
                address=request.POST.get('address', '')
            )

            # Auto login after signup
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()

    try:
        hotel = Hotel.objects.get(pk=1)  # or however you get your hotel instance
    except Hotel.DoesNotExist:
        hotel = None

    context = {
        'form': form,
        'hotel': hotel,
    }

    return render(request, 'signup.html', context)


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                next_url = request.GET.get('next', 'profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    try:
        hotel = Hotel.objects.get(pk=1)  # or however you get your hotel instance
    except Hotel.DoesNotExist:
        hotel = None

    context = {
        'form': form,
        'hotel': hotel,
    }

    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')


@login_required
def profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    # Get notification counts for this user
    count_pending_bookings = Booking.objects.filter(
        guest_email=request.user.email,
        status__in=['pending', 'confirmed']
    ).count()

    count_pending_reservations = ServiceReservation.objects.filter(
        guest_email=request.user.email,
        status__in=['pending', 'confirmed']
    ).count()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
        'hotel': Hotel.objects.first(),
        'count_pending_bookings': count_pending_bookings,
        'count_pending_reservations': count_pending_reservations,
    }
    return render(request, 'profile.html', context)


# my bookings
@login_required
def my_bookings(request):
    """
    Display all bookings for the logged-in user
    """
    # Get bookings for the logged-in user by email
    bookings = Booking.objects.filter(guest_email=request.user.email).order_by('-created_at')

    # Count pending bookings for notifications
    count_pending_bookings = Booking.objects.filter(
        guest_email=request.user.email,
        status__in=['pending', 'confirmed']
    ).count()

    count_pending_reservations = ServiceReservation.objects.filter(
        guest_email=request.user.email,
        status__in=['pending', 'confirmed']
    ).count()

    context = {
        'bookings': bookings,
        'count_pending_bookings': count_pending_bookings,
        'count_pending_reservations': count_pending_reservations,
        'hotel': Hotel.objects.first(),
    }
    return render(request, 'my_bookings.html', context)


@login_required
def booking_detail(request, booking_reference):
    """
    Display detailed view of a specific booking
    """
    booking = get_object_or_404(Booking, booking_reference=booking_reference, guest_email=request.user.email)

    context = {
        'booking': booking,
        'hotel': Hotel.objects.first(),
    }
    return render(request, 'booking_detail.html', context)


@login_required
def cancel_booking(request, booking_reference):
    """
    Cancel a booking (soft delete - change status to cancelled)
    """
    booking = get_object_or_404(Booking, booking_reference=booking_reference, guest_email=request.user.email)

    if request.method == 'POST':
        # Only allow cancellation for pending and confirmed bookings
        if booking.status in ['pending', 'confirmed']:
            booking.status = 'cancelled'
            booking.save()
            messages.success(request, f'Booking {booking_reference} has been cancelled successfully.')
        else:
            messages.error(request, 'This booking cannot be cancelled.')

        return redirect('my_bookings')

    context = {
        'booking': booking,
        'hotel': Hotel.objects.first(),
    }
    return render(request, 'cancel_booking.html', context)


# My service reservations
@login_required
def my_reservations(request):
    """
    Display all service reservations for the logged-in user
    """
    # Get service reservations for the logged-in user by email
    reservations = ServiceReservation.objects.filter(guest_email=request.user.email).order_by('-reservation_date',
                                                                                              '-reservation_time')

    context = {
        'reservations': reservations,
        'hotel': Hotel.objects.first(),
    }
    return render(request, 'my_reservations.html', context)


@login_required
def reservation_detail(request, reservation_number):
    """
    Display detailed view of a specific service reservation
    """
    reservation = get_object_or_404(ServiceReservation, reservation_number=reservation_number,
                                    guest_email=request.user.email)

    context = {
        'reservation': reservation,
        'hotel': Hotel.objects.first(),
    }
    return render(request, 'reservation_detail.html', context)


@login_required
def cancel_reservation(request, reservation_number):
    """
    Cancel a service reservation (change status to cancelled)
    """
    reservation = get_object_or_404(ServiceReservation, reservation_number=reservation_number,
                                    guest_email=request.user.email)

    if request.method == 'POST':
        # Only allow cancellation for pending and confirmed reservations
        if reservation.status in ['pending', 'confirmed']:
            reservation.status = 'cancelled'
            reservation.save()
            messages.success(request, f'Reservation {reservation_number} has been cancelled successfully.')
        else:
            messages.error(request, 'This reservation cannot be cancelled.')

        return redirect('my_reservations')

    context = {
        'reservation': reservation,
        'hotel': Hotel.objects.first(),
    }
    return render(request, 'cancel_reservation.html', context)


@login_required
def create_reservation(request):
    """
    Create a new service reservation
    """
    if request.method == 'POST':
        form = ServiceReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            # Auto-fill guest information from user profile
            reservation.guest_name = f"{request.user.first_name} {request.user.last_name}"
            reservation.guest_email = request.user.email
            if hasattr(request.user, 'profile'):
                reservation.guest_phone = request.user.profile.phone
            reservation.save()
            messages.success(request, 'Service reservation created successfully!')
            return redirect('my_reservations')
    else:
        form = ServiceReservationForm()

    context = {
        'form': form,
        'hotel': Hotel.objects.first(),
    }
    return render(request, 'create_reservation.html', context)


# Notifications
@login_required
def notifications_view(request):
    """
    Display all notifications for the logged-in user
    """
    # Check if user wants to mark all as viewed
    mark_viewed = request.GET.get('mark_viewed', False)

    if mark_viewed:
        # You could implement a simple session-based tracking
        request.session['notifications_last_viewed'] = timezone.now().isoformat()
        request.session.modified = True
        messages.success(request, 'All notifications marked as viewed.')
        return redirect('notifications')

    # Get pending and confirmed bookings
    pending_bookings = Booking.objects.filter(
        guest_email=request.user.email,
        status__in=['pending', 'confirmed']
    ).order_by('-created_at')

    # Get pending and confirmed service reservations
    pending_reservations = ServiceReservation.objects.filter(
        guest_email=request.user.email,
        status__in=['pending', 'confirmed']
    ).order_by('-created_at')

    # Get upcoming bookings (within next 7 days)
    upcoming_bookings = Booking.objects.filter(
        guest_email=request.user.email,
        status__in=['confirmed'],
        check_in__gte=timezone.now().date(),
        check_in__lte=timezone.now().date() + timezone.timedelta(days=7)
    ).order_by('check_in')

    # Get upcoming service reservations (within next 3 days)
    upcoming_reservations = ServiceReservation.objects.filter(
        guest_email=request.user.email,
        status__in=['confirmed'],
        reservation_date__gte=timezone.now().date(),
        reservation_date__lte=timezone.now().date() + timezone.timedelta(days=3)
    ).order_by('reservation_date', 'reservation_time')

    # Recent activity (last 30 days)
    recent_bookings = Booking.objects.filter(
        guest_email=request.user.email,
        created_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).order_by('-created_at')[:10]

    recent_reservations = ServiceReservation.objects.filter(
        guest_email=request.user.email,
        created_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).order_by('-created_at')[:10]

    # Check if there are new notifications since last view
    last_viewed = request.session.get('notifications_last_viewed')
    has_new_notifications = True  # Default to true

    if last_viewed:
        last_viewed_time = timezone.datetime.fromisoformat(last_viewed)
        # Check if any bookings/reservations were created after last view
        recent_count = (Booking.objects.filter(
            guest_email=request.user.email,
            created_at__gt=last_viewed_time
        ).count() + ServiceReservation.objects.filter(
            guest_email=request.user.email,
            created_at__gt=last_viewed_time
        ).count())
        has_new_notifications = recent_count > 0

    context = {
        'pending_bookings': pending_bookings,
        'pending_reservations': pending_reservations,
        'upcoming_bookings': upcoming_bookings,
        'upcoming_reservations': upcoming_reservations,
        'recent_bookings': recent_bookings,
        'recent_reservations': recent_reservations,
        'total_notifications': pending_bookings.count() + pending_reservations.count(),
        'has_new_notifications': has_new_notifications,
        'hotel': Hotel.objects.first(),
    }
    return render(request, 'notifications.html', context)


@login_required
def mark_notification_read(request, notification_type, item_id):
    """
    Mark specific notification as read (optional implementation)
    """
    # This could be expanded to track which notifications user has seen
    messages.success(request, 'Notification marked as read.')
    return redirect('notifications')


@login_required
def clear_all_notifications(request):
    """
    Clear all notifications (optional implementation)
    """
    # This could be expanded to track which notifications user has seen
    messages.success(request, 'All notifications cleared.')
    return redirect('notifications')


# Admin dashboard
@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard for staff users"""

    # Get date ranges
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Booking Statistics
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    confirmed_bookings = Booking.objects.filter(status='confirmed').count()
    today_bookings = Booking.objects.filter(created_at__date=today).count()
    upcoming_checkins = Booking.objects.filter(
        check_in=today,
        status='confirmed'
    ).count()

    # Service Reservation Statistics
    total_reservations = ServiceReservation.objects.count()
    pending_reservations = ServiceReservation.objects.filter(status='pending').count()
    confirmed_reservations = ServiceReservation.objects.filter(status='confirmed').count()
    today_reservations = ServiceReservation.objects.filter(created_at__date=today).count()

    # Payment Statistics
    total_booking_revenue = BookingPayment.objects.filter(
        payment_status='completed'
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    total_service_revenue = ServiceReservationPayment.objects.filter(
        payment_status='completed'
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    today_booking_revenue = BookingPayment.objects.filter(
        payment_status='completed',
        payment_date__date=today
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    today_service_revenue = ServiceReservationPayment.objects.filter(
        payment_status='completed',
        payment_date__date=today
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    # Contact and Blog Statistics
    unread_messages = ContactInquiry.objects.filter(is_resolved=False).count()
    total_subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()
    total_blog_posts = BlogPost.objects.count()
    published_posts = BlogPost.objects.filter(is_published=True).count()

    # Team Members
    active_team_members = TeamMember.objects.filter(is_active=True).count()

    # Recent Activity
    recent_bookings = Booking.objects.all().order_by('-created_at')[:5]
    recent_reservations = ServiceReservation.objects.all().order_by('-created_at')[:5]
    recent_messages = ContactInquiry.objects.filter(is_resolved=False).order_by('-created_at')[:5]
    recent_payments = list(BookingPayment.objects.filter(
        payment_status='completed'
    ).order_by('-payment_date')[:3]) + list(ServiceReservationPayment.objects.filter(
        payment_status='completed'
    ).order_by('-payment_date')[:2])

    # Sort combined payments by date
    recent_payments.sort(key=lambda x: x.payment_date, reverse=True)
    recent_payments = recent_payments[:5]

    # Chart data - Revenue last 7 days
    revenue_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        booking_rev = BookingPayment.objects.filter(
            payment_status='completed',
            payment_date__date=date
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

        service_rev = ServiceReservationPayment.objects.filter(
            payment_status='completed',
            payment_date__date=date
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

        revenue_data.append({
            'date': date.strftime('%a'),
            'booking': float(booking_rev),
            'service': float(service_rev),
            'total': float(booking_rev + service_rev)
        })

    # Notification counts for template
    pending_bookings_count = Booking.objects.filter(status='pending').count()
    pending_reservations_count = ServiceReservation.objects.filter(status='pending').count()
    unread_messages_count = ContactInquiry.objects.filter(is_resolved=False).count()

    # Handle Review model (check if it exists to avoid errors)
    try:
        new_reviews_count = Review.objects.filter(
            created_at__date=today,
            is_approved=False
        ).count()
    except:
        new_reviews_count = 0  # Fallback if Review model doesn't exist

    pending_booking_payments_count = BookingPayment.objects.filter(payment_status='pending').count()
    pending_service_payments_count = ServiceReservationPayment.objects.filter(payment_status='pending').count()

    total_admin_notifications = (
            pending_bookings_count +
            pending_reservations_count +
            unread_messages_count +
            new_reviews_count +
            pending_booking_payments_count +
            pending_service_payments_count
    )

    context = {
        # Statistics
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'today_bookings': today_bookings,
        'upcoming_checkins': upcoming_checkins,

        'total_reservations': total_reservations,
        'pending_reservations': pending_reservations,
        'confirmed_reservations': confirmed_reservations,
        'today_reservations': today_reservations,

        'total_booking_revenue': total_booking_revenue,
        'total_service_revenue': total_service_revenue,
        'today_booking_revenue': today_booking_revenue,
        'today_service_revenue': today_service_revenue,
        'total_revenue': total_booking_revenue + total_service_revenue,

        'unread_messages': unread_messages,
        'total_subscribers': total_subscribers,
        'total_blog_posts': total_blog_posts,
        'published_posts': published_posts,
        'active_team_members': active_team_members,

        # Recent Activity
        'recent_bookings': recent_bookings,
        'recent_reservations': recent_reservations,
        'recent_messages': recent_messages,
        'recent_payments': recent_payments,

        # Chart Data
        'revenue_data_json': json.dumps(revenue_data),

        'today': today,

        # Notification Counts
        'total_admin_notifications': total_admin_notifications,
        'pending_bookings_count': pending_bookings_count,
        'pending_reservations_count': pending_reservations_count,
        'unread_messages_count': unread_messages_count,
        'new_reviews_count': new_reviews_count,
        'pending_booking_payments_count': pending_booking_payments_count,
        'pending_service_payments_count': pending_service_payments_count,
    }

    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def admin_bookings(request):
    """Admin bookings management"""
    bookings = Booking.objects.all().order_by('-created_at')

    # Filtering
    status_filter = request.GET.get('status', '')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    # Pagination
    paginator = Paginator(bookings, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'bookings': page_obj,
        'status_filter': status_filter,
        'status_choices': Booking.BOOKING_STATUS,
    }
    return render(request, 'admin/bookings.html', context)


@staff_member_required
def admin_booking_detail(request, booking_id):
    """Admin booking detail view"""
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        # Update booking status
        new_status = request.POST.get('status')
        if new_status in dict(Booking.BOOKING_STATUS):
            booking.status = new_status
            booking.save()
            messages.success(request, f'Booking status updated to {booking.get_status_display()}')

        # Process payment
        if 'mark_paid' in request.POST and hasattr(booking, 'payment'):
            booking.payment.payment_status = 'completed'
            booking.payment.amount_paid = booking.total_price
            booking.payment.save()
            messages.success(request, 'Payment marked as completed')

        return redirect('admin_booking_detail', booking_id=booking.id)

    context = {
        'booking': booking,
    }
    return render(request, 'admin/booking_detail.html', context)


@staff_member_required
def admin_reservations(request):
    """Admin service reservations management"""
    reservations = ServiceReservation.objects.all().order_by('-created_at')

    # Filtering
    status_filter = request.GET.get('status', '')
    if status_filter:
        reservations = reservations.filter(status=status_filter)

    # Pagination
    paginator = Paginator(reservations, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'reservations': page_obj,
        'status_filter': status_filter,
        'status_choices': ServiceReservation.STATUS_CHOICES,
    }
    return render(request, 'admin/reservations.html', context)


@staff_member_required
def admin_reservation_detail(request, reservation_id):
    """Admin reservation detail view"""
    reservation = get_object_or_404(ServiceReservation, id=reservation_id)

    if request.method == 'POST':
        # Update reservation status
        new_status = request.POST.get('status')
        if new_status in dict(ServiceReservation.STATUS_CHOICES):
            reservation.status = new_status
            reservation.save()
            messages.success(request, f'Reservation status updated to {reservation.get_status_display()}')

        # Process payment
        if 'mark_paid' in request.POST:
            if hasattr(reservation, 'payment'):
                reservation.payment.payment_status = 'completed'
                reservation.payment.amount_paid = reservation.total_amount
                reservation.payment.save()
            else:
                ServiceReservationPayment.objects.create(
                    service_reservation=reservation,
                    amount_paid=reservation.total_amount,
                    payment_status='completed',
                    payment_method='cash'
                )
            messages.success(request, 'Payment marked as completed')

        return redirect('admin_reservation_detail', reservation_id=reservation.id)

    context = {
        'reservation': reservation,
    }
    return render(request, 'admin/reservation_detail.html', context)


@staff_member_required
def admin_messages(request):
    """Admin contact messages management"""
    messages_list = ContactInquiry.objects.all().order_by('-created_at')

    # Filtering
    resolved_filter = request.GET.get('resolved', '')
    if resolved_filter == 'unresolved':
        messages_list = messages_list.filter(is_resolved=False)
    elif resolved_filter == 'resolved':
        messages_list = messages_list.filter(is_resolved=True)

    type_filter = request.GET.get('type', '')
    if type_filter:
        messages_list = messages_list.filter(inquiry_type=type_filter)

    # Pagination
    paginator = Paginator(messages_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'messages': page_obj,
        'resolved_filter': resolved_filter,
        'type_filter': type_filter,
        'inquiry_types': ContactInquiry.INQUIRY_TYPES,
    }
    return render(request, 'admin/messages.html', context)


@staff_member_required
def admin_message_detail(request, message_id):
    """Admin message detail view"""
    message = get_object_or_404(ContactInquiry, id=message_id)

    if request.method == 'POST':
        # Mark as resolved/unresolved
        if 'mark_resolved' in request.POST:
            message.is_resolved = True
            message.resolved_notes = request.POST.get('resolved_notes', '')
            message.save()
            messages.success(request, 'Message marked as resolved')
        elif 'mark_unresolved' in request.POST:
            message.is_resolved = False
            message.save()
            messages.success(request, 'Message marked as unresolved')

        return redirect('admin_message_detail', message_id=message.id)

    context = {
        'message': message,
    }
    return render(request, 'admin/message_detail.html', context)


# PAYMENTS
@staff_member_required
def admin_payments(request):
    """Main payments dashboard"""
    # Pending payments counts for notifications
    pending_booking_payments = BookingPayment.objects.filter(payment_status='pending')
    pending_service_payments = ServiceReservationPayment.objects.filter(payment_status='pending')

    # Recent payments
    recent_booking_payments = BookingPayment.objects.select_related('booking').order_by('-payment_date')[:10]
    recent_service_payments = ServiceReservationPayment.objects.select_related('service_reservation').order_by(
        '-payment_date')[:10]

    # Payment statistics
    total_booking_revenue = BookingPayment.objects.filter(
        payment_status='completed'
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    total_service_revenue = ServiceReservationPayment.objects.filter(
        payment_status='completed'
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

    context = {
        'pending_booking_payments_count': pending_booking_payments.count(),
        'pending_service_payments_count': pending_service_payments.count(),
        'recent_booking_payments': recent_booking_payments,
        'recent_service_payments': recent_service_payments,
        'total_booking_revenue': total_booking_revenue,
        'total_service_revenue': total_service_revenue,
        'total_revenue': total_booking_revenue + total_service_revenue,
    }
    return render(request, 'admin/payments.html', context)


@staff_member_required
def booking_payments_list(request):
    """List all booking payments"""
    payments = BookingPayment.objects.select_related('booking').order_by('-payment_date')

    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(payment_status=status_filter)

    # Search
    search_query = request.GET.get('q')
    if search_query:
        payments = payments.filter(
            Q(booking__booking_reference__icontains=search_query) |
            Q(booking__guest_name__icontains=search_query) |
            Q(transaction_id__icontains=search_query)
        )

    # Calculate statistics
    total_revenue = payments.filter(payment_status='completed').aggregate(
        total=Sum('amount_paid')
    )['total'] or 0

    completed_count = payments.filter(payment_status='completed').count()
    pending_count = payments.filter(payment_status='pending').count()

    context = {
        'payments': payments,
        'status_filter': status_filter,
        'search_query': search_query or '',
        'total_revenue': total_revenue,
        'completed_count': completed_count,
        'pending_count': pending_count,
    }
    return render(request, 'admin/booking_payments_list.html', context)


@staff_member_required
def service_payments_list(request):
    """List all service reservation payments"""
    payments = ServiceReservationPayment.objects.select_related('service_reservation').order_by('-payment_date')

    # Filtering
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(payment_status=status_filter)

    # Search
    search_query = request.GET.get('q')
    if search_query:
        payments = payments.filter(
            Q(service_reservation__reservation_number__icontains=search_query) |
            Q(service_reservation__guest_name__icontains=search_query) |
            Q(transaction_id__icontains=search_query)
        )

    # Calculate statistics
    total_revenue = payments.filter(payment_status='completed').aggregate(
        total=Sum('amount_paid')
    )['total'] or 0

    completed_count = payments.filter(payment_status='completed').count()
    pending_count = payments.filter(payment_status='pending').count()

    context = {
        'payments': payments,
        'status_filter': status_filter,
        'search_query': search_query or '',
        'total_revenue': total_revenue,
        'completed_count': completed_count,
        'pending_count': pending_count,
    }
    return render(request, 'admin/service_payments_list.html', context)


@staff_member_required
def receive_booking_payment(request, booking_reference):
    """Receive payment for a specific booking"""
    booking = get_object_or_404(Booking, booking_reference=booking_reference)

    # Check if payment already exists
    try:
        payment = booking.payment
        form = BookingPaymentForm(request.POST or None, instance=payment)
    except BookingPayment.DoesNotExist:
        payment = None
        form = BookingPaymentForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            payment_instance = form.save(commit=False)
            payment_instance.booking = booking

            # Set amount paid to total price if not specified
            if not payment_instance.amount_paid:
                payment_instance.amount_paid = booking.total_price

            payment_instance.save()

            # Update booking status if payment is completed
            if payment_instance.payment_status == 'completed' and booking.status == 'pending':
                booking.status = 'confirmed'
                booking.save()
                messages.success(request, f'Payment received and booking confirmed!')
            else:
                messages.success(request, f'Payment recorded for booking {booking_reference}')

            return redirect('admin_booking_payments')

    context = {
        'booking': booking,
        'form': form,
        'payment': payment,
    }
    return render(request, 'admin/receive_booking_payment.html', context)


@staff_member_required
def receive_service_payment(request, reservation_number):
    """Receive payment for a specific service reservation"""
    reservation = get_object_or_404(ServiceReservation, reservation_number=reservation_number)

    # Check if payment already exists
    try:
        payment = reservation.payment
        form = ServiceReservationPaymentForm(request.POST or None, instance=payment)
    except ServiceReservationPayment.DoesNotExist:
        payment = None
        form = ServiceReservationPaymentForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            payment_instance = form.save(commit=False)
            payment_instance.service_reservation = reservation

            # Set amount paid to total amount if not specified
            if not payment_instance.amount_paid:
                payment_instance.amount_paid = reservation.total_amount

            payment_instance.save()

            # Update reservation status if payment is completed
            if payment_instance.payment_status == 'completed' and reservation.status == 'pending':
                reservation.status = 'confirmed'
                reservation.save()
                messages.success(request, f'Payment received and reservation confirmed!')
            else:
                messages.success(request, f'Payment recorded for reservation {reservation_number}')

            return redirect('admin_service_payments')

    context = {
        'reservation': reservation,
        'form': form,
        'payment': payment,
    }
    return render(request, 'admin/receive_service_payment.html', context)


@staff_member_required
def edit_booking_payment(request, payment_id):
    """Edit an existing booking payment"""
    payment = get_object_or_404(BookingPayment, id=payment_id)

    if request.method == 'POST':
        form = BookingPaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()

            # Update booking status if needed
            booking = payment.booking
            if payment.payment_status == 'completed' and booking.status == 'pending':
                booking.status = 'confirmed'
                booking.save()
                messages.success(request, 'Payment updated and booking confirmed!')
            else:
                messages.success(request, 'Payment updated successfully!')

            return redirect('admin_booking_payments')
    else:
        form = BookingPaymentForm(instance=payment)

    context = {
        'form': form,
        'payment': payment,
        'booking': payment.booking,
    }
    return render(request, 'admin/edit_booking_payment.html', context)


@staff_member_required
def edit_service_payment(request, payment_id):
    """Edit an existing service payment"""
    payment = get_object_or_404(ServiceReservationPayment, id=payment_id)

    if request.method == 'POST':
        form = ServiceReservationPaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()

            # Update reservation status if needed
            reservation = payment.service_reservation
            if payment.payment_status == 'completed' and reservation.status == 'pending':
                reservation.status = 'confirmed'
                reservation.save()
                messages.success(request, 'Payment updated and reservation confirmed!')
            else:
                messages.success(request, 'Payment updated successfully!')

            return redirect('admin_service_payments')
    else:
        form = ServiceReservationPaymentForm(instance=payment)

    context = {
        'form': form,
        'payment': payment,
        'reservation': payment.service_reservation,
    }
    return render(request, 'admin/edit_service_payment.html', context)


@staff_member_required
def admin_blog(request):
    """Admin blog management"""
    posts = BlogPost.objects.all().order_by('-created_at')

    # Filtering
    published_filter = request.GET.get('published', '')
    if published_filter == 'published':
        posts = posts.filter(is_published=True)
    elif published_filter == 'draft':
        posts = posts.filter(is_published=False)

    category_filter = request.GET.get('category', '')
    if category_filter:
        posts = posts.filter(category_id=category_filter)

    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = BlogCategory.objects.all()

    context = {
        'posts': page_obj,
        'categories': categories,
        'published_filter': published_filter,
        'category_filter': category_filter,
    }
    return render(request, 'admin/blog.html', context)


@staff_member_required
def admin_blog_create(request):
    """Create new blog post"""
    from blog.forms import BlogPostForm

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            if post.is_published and not post.published_date:
                post.published_date = timezone.now()
            post.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('admin_blog')
    else:
        form = BlogPostForm()

    context = {
        'form': form,
        'title': 'Create New Blog Post',
    }
    return render(request, 'admin/blog_form.html', context)


@staff_member_required
def admin_blog_edit(request, post_id):
    """Edit blog post"""
    from blog.forms import BlogPostForm
    post = get_object_or_404(BlogPost, id=post_id)

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            if post.is_published and not post.published_date:
                post.published_date = timezone.now()
            post.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('admin_blog')
    else:
        form = BlogPostForm(instance=post)

    context = {
        'form': form,
        'title': 'Edit Blog Post',
        'post': post,
    }
    return render(request, 'admin/blog_form.html', context)


@staff_member_required
def admin_team(request):
    """Admin team management"""
    team_members = TeamMember.objects.all().order_by('display_order', 'name')

    context = {
        'team_members': team_members,
    }
    return render(request, 'admin/team.html', context)


@staff_member_required
def admin_team_create(request):
    """Create new team member"""
    from hotel.forms import TeamMemberForm

    # Get the hotel (you might need to adjust this based on your setup)
    hotel = Hotel.objects.first()  # Or get from request/session/context

    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            team_member = form.save(commit=False)
            team_member.hotel = hotel
            team_member.save()
            messages.success(request, 'Team member added successfully!')
            return redirect('admin_team')
    else:
        form = TeamMemberForm(initial={'hotel': hotel})

    context = {
        'form': form,
        'title': 'Add New Team Member',
        'hotel': hotel,
    }
    return render(request, 'admin/team_form.html', context)


@staff_member_required
def admin_team_edit(request, member_id):
    """Edit team member"""
    from hotel.forms import TeamMemberForm
    member = get_object_or_404(TeamMember, id=member_id)

    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Team member updated successfully!')
            return redirect('admin_team')
    else:
        form = TeamMemberForm(instance=member)

    context = {
        'form': form,
        'title': 'Edit Team Member',
        'member': member,
    }
    return render(request, 'admin/team_form.html', context)


@staff_member_required
def admin_reports(request):
    """Admin reports and analytics"""
    # Date range for reports
    start_date = request.GET.get('start_date', (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.GET.get('end_date', timezone.now().strftime('%Y-%m-%d'))

    try:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date_obj = timezone.now().date() - timedelta(days=30)
        end_date_obj = timezone.now().date()

    # Booking reports
    booking_stats = Booking.objects.filter(
        created_at__date__range=[start_date_obj, end_date_obj]
    ).aggregate(
        total=Count('id'),
        total_revenue=Sum('total_price'),
        confirmed=Count('id', filter=Q(status='confirmed')),
        pending=Count('id', filter=Q(status='pending'))
    )

    # Payment reports - CORRECTED VERSION
    booking_payments_agg = BookingPayment.objects.filter(
        payment_date__date__range=[start_date_obj, end_date_obj],
        payment_status='completed'
    ).aggregate(total=Sum('amount_paid'))

    service_payments_agg = ServiceReservationPayment.objects.filter(
        payment_date__date__range=[start_date_obj, end_date_obj],
        payment_status='completed'
    ).aggregate(total=Sum('amount_paid'))

    payment_stats = {
        'booking_payments': booking_payments_agg['total'] or 0,
        'service_payments': service_payments_agg['total'] or 0,
    }

    context = {
        'start_date': start_date_obj,
        'end_date': end_date_obj,
        'booking_stats': booking_stats,
        'payment_stats': payment_stats,
        'total_revenue': payment_stats['booking_payments'] + payment_stats['service_payments'],
    }
    return render(request, 'admin/reports.html', context)


# Get Real Time Notifications
def get_admin_notification_counts(request):
    """Get real-time notification counts for admin dashboard"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Calculate counts for different notification types
    pending_bookings_count = Booking.objects.filter(status='pending').count()
    pending_reservations_count = ServiceReservation.objects.filter(status='pending').count()
    unread_messages_count = ContactInquiry.objects.filter(is_resolved=False).count()

    # New reviews (last 24 hours)
    today = timezone.now().date()
    new_reviews_count = Review.objects.filter(
        created_at__date=today,
        is_approved=False
    ).count()

    # Pending payments
    pending_booking_payments_count = BookingPayment.objects.filter(
        payment_status='pending'
    ).count()

    pending_service_payments_count = ServiceReservationPayment.objects.filter(
        payment_status='pending'
    ).count()

    # Total notifications
    total_admin_notifications = (
            pending_bookings_count +
            pending_reservations_count +
            unread_messages_count +
            new_reviews_count +
            pending_booking_payments_count +
            pending_service_payments_count
    )

    return JsonResponse({
        'total_admin_notifications': total_admin_notifications,
        'pending_bookings_count': pending_bookings_count,
        'pending_reservations_count': pending_reservations_count,
        'unread_messages_count': unread_messages_count,
        'new_reviews_count': new_reviews_count,
        'pending_booking_payments_count': pending_booking_payments_count,
        'pending_service_payments_count': pending_service_payments_count,
        'last_checked': timezone.now().isoformat()
    })


def get_recent_notifications(request):
    """Get recent notifications for dropdown"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    recent_notifications = []

    # Recent pending bookings (last 2 hours)
    two_hours_ago = timezone.now() - timedelta(hours=2)
    recent_bookings = Booking.objects.filter(
        status='pending',
        created_at__gte=two_hours_ago
    )[:5]

    for booking in recent_bookings:
        recent_notifications.append({
            'type': 'booking',
            'title': f'New Booking from {booking.guest_name}',
            'message': f'Room: {booking.room.room_type}',
            'time': booking.created_at,
            'url': f'/admin/bookings/{booking.id}/',
            'priority': 'high'
        })

    # Recent pending reservations
    recent_reservations = ServiceReservation.objects.filter(
        status='pending',
        created_at__gte=two_hours_ago
    )[:5]

    for reservation in recent_reservations:
        recent_notifications.append({
            'type': 'reservation',
            'title': f'New Service Reservation',
            'message': f'{reservation.service.name} for {reservation.guest_name}',
            'time': reservation.created_at,
            'url': f'/admin/reservations/{reservation.id}/',
            'priority': 'medium'
        })

    # Recent unread messages
    recent_messages = ContactInquiry.objects.filter(
        is_resolved=False,
        created_at__gte=two_hours_ago
    )[:5]

    for message in recent_messages:
        recent_notifications.append({
            'type': 'message',
            'title': f'New Message: {message.subject}',
            'message': f'From: {message.name}',
            'time': message.created_at,
            'url': f'/admin/messages/{message.id}/',
            'priority': 'medium'
        })

    # Recent reviews
    recent_reviews = Review.objects.filter(
        created_at__gte=two_hours_ago,
        is_approved=False
    )[:5]

    for review in recent_reviews:
        recent_notifications.append({
            'type': 'review',
            'title': f'New Review from {review.user.get_full_name()}',
            'message': f'Rating: {review.rating}/5',
            'time': review.created_at,
            'url': f'/admin/reviews/{review.id}/',
            'priority': 'low'
        })

    # Sort by time (newest first)
    recent_notifications.sort(key=lambda x: x['time'], reverse=True)

    # Convert to serializable format
    for notification in recent_notifications:
        notification['time'] = notification['time'].isoformat()
        notification['time_ago'] = timesince(notification['time'])

    return JsonResponse({
        'notifications': recent_notifications[:10],  # Limit to 10 most recent
        'total_count': len(recent_notifications)
    })


# EVENTS
# Admin views
def is_staff(user):
    return user.is_staff


@login_required
@user_passes_test(is_staff)
def admin_events(request):
    events = Event.objects.all().order_by('-created_at')
    context = {
        'events': events,
    }
    return render(request, 'admin/admin_events.html', context)


@login_required
@user_passes_test(is_staff)
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('admin_events')
    else:
        form = EventForm()

    context = {
        'form': form,
        'title': 'Create New Event'
    }
    return render(request, 'admin/event_form.html', context)


@login_required
@user_passes_test(is_staff)
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('admin_events')
    else:
        form = EventForm(instance=event)

    context = {
        'form': form,
        'title': 'Edit Event',
        'event': event
    }
    return render(request, 'admin/event_form.html', context)


@login_required
@user_passes_test(is_staff)
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('admin_events')

    context = {
        'event': event
    }
    return render(request, 'admin/confirm_delete.html', context)



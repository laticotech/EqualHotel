from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import *
from rooms.models import *
from accounts.models import User, Profile
from gallery.models import *
from services.models import *
from bookings.models import Booking
from reviews.models import Review
from .forms import *


# Create your views here.
def index(request):
    hotel = Hotel.objects.get(pk=1)

    # Get featured gallery images for the slider
    featured_gallery_images = GalleryImage.objects.filter(
        is_featured=True
    ).select_related('category').order_by('display_order')[:6]

    # Get available room types for booking section
    available_room_types = RoomType.objects.filter(
        is_available=True
    ).order_by('display_order', 'base_price')[:4]

    # Get active services for services section
    active_services = Service.objects.filter(
        is_active=True
    ).order_by('display_order', 'name')[:3]

    # FIXED: Handle case where user is not authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = Profile.objects.create(user=request.user)
    # If user is not authenticated, profile remains None

    # Get amenities (optional - you can also access via hotel.amenities.all in template)
    amenities = hotel.amenities.all().order_by('category', 'name')

    home = "home"
    """Display all approved reviews"""
    reviews = Review.objects.filter(is_approved=True).order_by('-created_at')

    # Calculate average rating
    total_reviews = reviews.count()
    if total_reviews > 0:
        average_rating = sum(review.rating for review in reviews) / total_reviews
    else:
        average_rating = 0

    # Get rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = reviews.filter(rating=i).count()

    # Featured reviews for carousel
    featured_reviews = reviews.filter(is_featured=True)[:5]

    context = {
        'profile': profile,  # This can be None if user is not logged in
        'hotel': hotel,
        'home': home,
        'gallery': featured_gallery_images,
        'room_types': available_room_types,
        'services': active_services,
        'amenities': amenities,  # Optional: pass explicitly to context
        'reviews': reviews,
        'featured_reviews': featured_reviews,
        'total_reviews': total_reviews,
        'average_rating': round(average_rating, 1),
        'rating_distribution': rating_distribution,
    }
    return render(request, 'index.html', context)


def all_amenities(request):
    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    amenity = 'amenity'
    # Group amenities by category for the template
    amenities_by_category = {}
    for amenity in hotel.amenities.all().order_by('category', 'name'):
        category_name = amenity.get_category_display()
        if category_name not in amenities_by_category:
            amenities_by_category[category_name] = []
        amenities_by_category[category_name].append(amenity)

    context = {
        'hotel': hotel,
        'profile': profile,
        'amenity': amenity,
        'amenities_by_category': amenities_by_category,
    }
    return render(request, 'all_amenities.html', context)


def about_us(request):
    """
    Display about us page with hotel information, policies, and video
    """
    try:
        hotel = Hotel.objects.get(pk=1)  # Get the main hotel instance
    except Hotel.DoesNotExist:
        hotel = None

    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None

    context = {
        'hotel': hotel,
        'profile': profile,
        'about': 'active',  # For active navigation highlighting
    }
    return render(request, 'about.html', context)


def is_staff(user):
    return user.is_staff


# Public view for all events
def events_list(request):
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        start_date__gte=now,
        is_active=True
    ).order_by('start_date')
    our_events = 'our_events'
    context = {
        'our_events': our_events,
        'upcoming_events': upcoming_events,
        'events': upcoming_events,  # For your menu badge
    }
    return render(request, 'events_list.html', context)


# Public view for event detail
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_active=True)
    other_events = Event.objects.filter(
        is_active=True,
        start_date__gte=timezone.now()
    ).exclude(id=event_id).order_by('start_date')[:3]

    user_registration = None
    if request.user.is_authenticated:
        user_registration = EventRegistration.objects.filter(
            event=event,
            email=request.user.email
        ).first()

    context = {
        'event': event,
        'other_events': other_events,
        'user_registration': user_registration,
    }
    return render(request, 'event_detail.html', context)


def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id, is_active=True)

    # Check if event is full
    if event.is_full:
        messages.error(request, "This event is fully booked. Please check back for future events.")
        return redirect('event_detail', event_id=event_id)

    # Check if user is already registered
    if request.user.is_authenticated:
        existing_registration = EventRegistration.objects.filter(
            event=event,
            email=request.user.email
        ).first()
    else:
        existing_registration = None

    if request.method == 'POST':
        # Pass the event to the form
        form = EventRegistrationForm(request.POST, event=event)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.event = event
            if request.user.is_authenticated:
                registration.user = request.user
                # Use authenticated user's email if not already set
                if not registration.email:
                    registration.email = request.user.email

            # Auto-confirm if payment not required
            if event.price == 0:
                registration.status = 'confirmed'
                registration.confirmation_date = timezone.now()

            registration.save()

            # Send confirmation email
            send_registration_confirmation(registration, request)

            messages.success(request, f"Successfully registered for {event.title}!")
            return redirect('registration_success', registration_id=registration.id)
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        # Pass the event to the form
        form = EventRegistrationForm(initial=initial_data, event=event)

    context = {
        'event': event,
        'form': form,
        'existing_registration': existing_registration,
    }
    return render(request, 'event_registration.html', context)


def registration_success(request, registration_id):
    registration = get_object_or_404(EventRegistration, id=registration_id)
    context = {
        'registration': registration,
    }
    return render(request, 'registration_success.html', context)


def my_event_registrations(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Please log in to view your event registrations.")
        return redirect('login')

    registrations = EventRegistration.objects.filter(
        email=request.user.email
    ).select_related('event').order_by('-registration_date')

    context = {
        'registrations': registrations,
    }
    return render(request, 'my_registrations.html', context)


def cancel_registration(request, registration_id):
    if not request.user.is_authenticated:
        messages.error(request, "Please log in to cancel your registration.")
        return redirect('login')

    registration = get_object_or_404(
        EventRegistration,
        id=registration_id,
        email=request.user.email
    )

    if request.method == 'POST':
        registration.status = 'cancelled'
        registration.save()

        # Send cancellation email
        send_cancellation_notification(registration, request)

        messages.success(request, f"Your registration for {registration.event.title} has been cancelled.")
        return redirect('my_event_registrations')

    context = {
        'registration': registration,
    }
    return render(request, 'cancel_registration.html', context)


# Email functions
def send_registration_confirmation(registration, request):
    subject = f"Event Registration Confirmation - {registration.event.title}"

    context = {
        'registration': registration,
        'event': registration.event,
        'site_url': request.build_absolute_uri('/')[:-1],
    }

    html_message = render_to_string('emails/registration_confirmation.html', context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=None,  # Uses DEFAULT_FROM_EMAIL from settings
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )
        registration.confirmation_sent = True
        registration.save(update_fields=['confirmation_sent'])
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")


def send_cancellation_notification(registration, request):
    subject = f"Event Registration Cancelled - {registration.event.title}"

    context = {
        'registration': registration,
        'event': registration.event,
    }

    html_message = render_to_string('emails/registration_cancelled.html', context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=None,
            recipient_list=[registration.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send cancellation email: {e}")
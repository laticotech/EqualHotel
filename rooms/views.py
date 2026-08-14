from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Min, Max
from django.core.paginator import Paginator
from .models import RoomType, Room, RoomAmenity
from hotel.models import Hotel
from accounts.models import User, Profile


def room_list(request):
    """View for displaying rooms with filtering options"""
    # Get all available room types
    room_types = RoomType.objects.filter(is_available=True).order_by('display_order', 'base_price')

    # Get filter parameters with proper default values
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    capacity = request.GET.get('capacity', '')
    bed_type = request.GET.get('bed_type', '')
    search_query = request.GET.get('search', '')  # Default to empty string

    # Apply filters (only if values are provided)
    if price_min:
        room_types = room_types.filter(base_price__gte=price_min)
    if price_max:
        room_types = room_types.filter(base_price__lte=price_max)
    if capacity:
        room_types = room_types.filter(capacity__gte=capacity)
    if bed_type:
        room_types = room_types.filter(bed_type__icontains=bed_type)
    if search_query:  # Only search if there's actually a query
        room_types = room_types.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(special_features__icontains=search_query)
        )

    # ... rest of your view code remains the same
    # Get available bed types for filter
    available_bed_types = RoomType.objects.filter(
        is_available=True
    ).exclude(bed_type='').values_list('bed_type', flat=True).distinct()

    # Get price range for filter
    price_range = RoomType.objects.filter(is_available=True).aggregate(
        min_price=Min('base_price'),
        max_price=Max('base_price')
    )

    # Pagination
    paginator = Paginator(room_types, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
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
        'hotel': hotel,
        'room': room,
        'profile': profile,
        'room_types': page_obj,
        'available_bed_types': available_bed_types,
        'price_range': price_range,
        'current_filters': {
            'price_min': price_min,
            'price_max': price_max,
            'capacity': capacity,
            'bed_type': bed_type,
            'search': search_query,  # This will now be empty string instead of None
        }
    }

    return render(request, 'accommodations.html', context)


def room_detail(request, slug):
    """View for individual room type details"""
    room_type = get_object_or_404(RoomType, slug=slug, is_available=True)
    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None

    # Get available rooms of this type
    available_rooms = room_type.rooms.filter(is_available=True)

    # Get room images
    room_images = room_type.images.all()

    # Get amenities
    amenities = room_type.amenities.all()

    # Get other available room types (for sidebar)
    other_rooms = RoomType.objects.filter(
        is_available=True
    ).exclude(id=room_type.id).order_by('display_order', 'base_price')[:3]
    room = 'room'
    context = {
        'hotel': hotel,
        'room': room,
        'profile': profile,
        'room_type': room_type,
        'available_rooms': available_rooms,
        'room_images': room_images,
        'amenities': amenities,
        'other_rooms': other_rooms,
    }

    return render(request, 'accommodation_details.html', context)  # Make sure this matches your template name


def room_detail_json(request, slug):
    """JSON API view for room details"""
    room_type = get_object_or_404(RoomType, slug=slug, is_available=True)

    # Get available rooms
    available_rooms = list(room_type.rooms.filter(is_available=True).values(
        'room_number', 'floor', 'view_description'
    ))

    # Get room images
    room_images = list(room_type.images.values('image', 'caption', 'is_featured'))

    # Get amenities
    amenities = list(room_type.amenities.values('name', 'icon'))

    data = {
        'success': True,
        'room_type': {
            'id': room_type.id,
            'name': room_type.name,
            'slug': room_type.slug,
            'description': room_type.description,
            'base_price': str(room_type.base_price),
            'capacity': room_type.capacity,
            'size': room_type.size,
            'bed_type': room_type.bed_type,
            'featured_image': room_type.featured_image.url if room_type.featured_image else None,
        },
        'available_rooms': available_rooms,
        'room_images': room_images,
        'amenities': amenities,
        'total_available_rooms': len(available_rooms),
    }

    return JsonResponse(data)


def room_availability_json(request):
    """JSON API for checking room availability with filters"""
    room_types = RoomType.objects.filter(is_available=True)

    # Apply filters from request
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    capacity = request.GET.get('capacity')

    if price_min:
        room_types = room_types.filter(base_price__gte=float(price_min))
    if price_max:
        room_types = room_types.filter(base_price__lte=float(price_max))
    if capacity:
        room_types = room_types.filter(capacity__gte=int(capacity))

    rooms_data = []
    for room_type in room_types:
        available_count = room_type.rooms.filter(is_available=True).count()

        rooms_data.append({
            'id': room_type.id,
            'name': room_type.name,
            'slug': room_type.slug,
            'base_price': str(room_type.base_price),
            'capacity': room_type.capacity,
            'size': room_type.size,
            'bed_type': room_type.bed_type,
            'available_rooms': available_count,
            'featured_image': room_type.featured_image.url if room_type.featured_image else None,
        })

    return JsonResponse({
        'success': True,
        'rooms': rooms_data,
        'total_rooms': len(rooms_data)
    })


def room_search_json(request):
    """JSON API for room search"""
    query = request.GET.get('q', '')

    if not query:
        return JsonResponse({'success': False, 'error': 'No search query provided'})

    room_types = RoomType.objects.filter(
        Q(is_available=True) &
        (Q(name__icontains=query) |
         Q(description__icontains=query) |
         Q(bed_type__icontains=query) |
         Q(special_features__icontains=query))
    )[:10]  # Limit results

    results = []
    for room_type in room_types:
        results.append({
            'id': room_type.id,
            'name': room_type.name,
            'slug': room_type.slug,
            'base_price': str(room_type.base_price),
            'capacity': room_type.capacity,
            'bed_type': room_type.bed_type,
            'featured_image': room_type.featured_image.url if room_type.featured_image else None,
            'url': f'/rooms/{room_type.slug}/'
        })

    return JsonResponse({
        'success': True,
        'query': query,
        'results': results,
        'count': len(results)
    })
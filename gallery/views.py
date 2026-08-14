# gallery/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import GalleryCategory, GalleryImage
from hotel.models import Hotel
from accounts.models import User, Profile


def gallery_list(request):
    """
    Main gallery page showing all categories and featured images
    """
    # Get all categories with their images
    categories = GalleryCategory.objects.prefetch_related('images').all()
    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    more = 'more'
    # Get featured images for the hero section
    featured_images = GalleryImage.objects.filter(
        is_featured=True
    ).select_related('category').order_by('display_order')[:8]

    # Get recent images
    recent_images = GalleryImage.objects.select_related('category').order_by('-uploaded_at')[:12]

    context = {
        'hotel': hotel,
        'profile': profile,
        'more': more,
        'categories': categories,
        'featured_images': featured_images,
        'recent_images': recent_images,
        'gallery': 'gallery',  # For active menu highlighting
    }
    return render(request, 'gallery_list.html', context)


def gallery_category(request, category_id):
    """
    View images by specific category
    """
    category = get_object_or_404(GalleryCategory, id=category_id)

    # Get all images for this category
    images = GalleryImage.objects.filter(
        category=category
    ).select_related('category').order_by('display_order', '-uploaded_at')

    # Pagination
    paginator = Paginator(images, 12)  # 12 images per page
    page = request.GET.get('page')

    try:
        images_page = paginator.page(page)
    except PageNotAnInteger:
        images_page = paginator.page(1)
    except EmptyPage:
        images_page = paginator.page(paginator.num_pages)

    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    more = 'more'
    context = {
        'category': category,
        'images': images_page,
        'gallery': gallery,
        'hotel': hotel,
        'profile': profile,
        'more': more,
    }
    return render(request, 'gallery_category.html', context)


def gallery_image_detail(request, image_id):
    """
    Detailed view for a single image with navigation
    """
    image = get_object_or_404(GalleryImage, id=image_id)
    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    more = 'more'

    # Get previous and next images for navigation
    previous_image = GalleryImage.objects.filter(
        category=image.category,
        display_order__lt=image.display_order
    ).order_by('-display_order').first()

    next_image = GalleryImage.objects.filter(
        category=image.category,
        display_order__gt=image.display_order
    ).order_by('display_order').first()

    # Get related images from same category
    related_images = GalleryImage.objects.filter(
        category=image.category
    ).exclude(id=image.id).order_by('display_order')[:6]

    context = {
        'hotel': hotel,
        'profile': profile,
        'more': more,
        'image': image,
        'previous_image': previous_image,
        'next_image': next_image,
        'related_images': related_images,
        'gallery': 'gallery',
    }
    return render(request, 'gallery_detail.html', context)


def gallery_featured(request):
    """
    View all featured images
    """
    featured_images = GalleryImage.objects.filter(
        is_featured=True
    ).select_related('category').order_by('display_order', '-uploaded_at')
    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    more = 'more'
    # Pagination
    paginator = Paginator(featured_images, 16)  # 16 images per page
    page = request.GET.get('page')

    try:
        images_page = paginator.page(page)
    except PageNotAnInteger:
        images_page = paginator.page(1)
    except EmptyPage:
        images_page = paginator.page(paginator.num_pages)

    context = {
        'images': images_page,
        'title': 'Featured Gallery',
        'gallery': 'gallery',
        'hotel': hotel,
        'profile': profile,
        'more': more,
    }
    return render(request, 'gallery_featured.html', context)


def gallery_search(request):
    """
    Search gallery images by title or caption
    """
    query = request.GET.get('q', '')
    images = GalleryImage.objects.all()

    if query:
        images = images.filter(
            models.Q(title__icontains=query) |
            models.Q(caption__icontains=query) |
            models.Q(category__name__icontains=query)
        ).select_related('category').order_by('display_order', '-uploaded_at')

    # Pagination
    paginator = Paginator(images, 12)
    page = request.GET.get('page')

    try:
        images_page = paginator.page(page)
    except PageNotAnInteger:
        images_page = paginator.page(1)
    except EmptyPage:
        images_page = paginator.page(paginator.num_pages)
    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    more = 'more'
    context = {
        'hotel': hotel,
        'profile': profile,
        'more': more,
        'images': images_page,
        'query': query,
        'title': f'Search Results for "{query}"' if query else 'Search Gallery',
        'gallery': 'gallery',
    }
    return render(request, 'gallery_search.html', context)
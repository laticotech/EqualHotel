from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost, BlogCategory
from hotel.models import Hotel
from accounts.models import User, Profile


def blog_list(request):
    """
    Display all published blog posts with pagination
    """
    # Get published posts ordered by published date
    blog_posts = BlogPost.objects.filter(is_published=True).order_by('-published_date')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        blog_posts = blog_posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    # Category filter
    category_slug = request.GET.get('category', '')
    if category_slug:
        blog_posts = blog_posts.filter(category__slug=category_slug)

    # Pagination
    paginator = Paginator(blog_posts, 6)  # 6 posts per page
    page = request.GET.get('page')
    posts_page = paginator.get_page(page)

    # Get all categories for sidebar
    categories = BlogCategory.objects.all()

    # Get recent posts for sidebar
    recent_posts = BlogPost.objects.filter(is_published=True).order_by('-published_date')[:5]

    try:
        hotel = Hotel.objects.get(pk=1)  # or however you get your hotel instance
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
        'posts': posts_page,
        'categories': categories,
        'recent_posts': recent_posts,
        'search_query': search_query,
        'selected_category': category_slug,
        'blog': 'active',  # For active navigation
    }
    return render(request, 'blog_list.html', context)


def blog_detail(request, slug):
    """
    Display individual blog post
    """
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)

    # Get related posts (same category)
    related_posts = BlogPost.objects.filter(
        category=post.category,
        is_published=True
    ).exclude(id=post.id).order_by('-published_date')[:3]

    # Get recent posts for sidebar
    recent_posts = BlogPost.objects.filter(is_published=True).exclude(id=post.id).order_by('-published_date')[:5]

    # Get categories for sidebar
    categories = BlogCategory.objects.all()
    try:
        hotel = Hotel.objects.get(pk=1)  # or however you get your hotel instance
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
        'post': post,
        'hotel': hotel,
        'profile': profile,
        'related_posts': related_posts,
        'recent_posts': recent_posts,
        'categories': categories,
        'blog': 'active',
    }
    return render(request, 'blog_detail.html', context)


def blog_category(request, slug):
    """
    Display blog posts by category
    """
    category = get_object_or_404(BlogCategory, slug=slug)
    blog_posts = BlogPost.objects.filter(category=category, is_published=True).order_by('-published_date')

    # Pagination
    paginator = Paginator(blog_posts, 6)
    page = request.GET.get('page')
    posts_page = paginator.get_page(page)

    # Get all categories for sidebar
    categories = BlogCategory.objects.all()

    # Get recent posts for sidebar
    recent_posts = BlogPost.objects.filter(is_published=True).order_by('-published_date')[:5]
    try:
        hotel = Hotel.objects.get(pk=1)  # or however you get your hotel instance
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
        'posts': posts_page,
        'category': category,
        'categories': categories,
        'recent_posts': recent_posts,
        'selected_category': slug,
        'blog': 'active',
    }
    return render(request, 'blog_category.html', context)
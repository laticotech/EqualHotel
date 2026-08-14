from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Review
from .forms import ReviewForm
from accounts.models import User, Profile
from hotel.models import Hotel


# Public Views
def reviews_list(request):
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

    # Pagination
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page')
    reviews_page = paginator.get_page(page)

    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    context = {
        'reviews': reviews_page,
        'featured_reviews': featured_reviews,
        'total_reviews': total_reviews,
        'average_rating': round(average_rating, 1),
        'rating_distribution': rating_distribution,
        'reviews_active': 'active',
        'hotel': hotel,
        'profile': profile,
    }
    return render(request, 'reviews_list.html', context)


@login_required()
def submit_review(request):
    """Handle review submission"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            # Auto-approve if you want, or keep for moderation
            # review.is_approved = True
            review.save()
            messages.success(request, 'Thank you for your review! It will be published after moderation.')
            return redirect('reviews_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm()
    hotel = Hotel.objects.get(pk=1)
    # Only get profile if user is authenticated
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    context = {
        'form': form,
        'hotel': hotel,
        'profile': profile,
        'reviews_active': 'active',
    }
    return render(request, 'submit_review.html', context)


# Admin Views
class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'reviews/admin/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 15
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by approval status
        status = self.request.GET.get('status')
        if status == 'approved':
            queryset = queryset.filter(is_approved=True)
        elif status == 'pending':
            queryset = queryset.filter(is_approved=False)

        # Filter by featured status
        featured = self.request.GET.get('featured')
        if featured == 'featured':
            queryset = queryset.filter(is_featured=True)
        elif featured == 'not_featured':
            queryset = queryset.filter(is_featured=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_reviews'] = Review.objects.count()
        context['approved_reviews'] = Review.objects.filter(is_approved=True).count()
        context['pending_reviews'] = Review.objects.filter(is_approved=False).count()
        context['featured_reviews'] = Review.objects.filter(is_featured=True).count()
        return context


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    template_name = 'reviews/admin/review_form.html'
    form_class = ReviewForm
    success_url = reverse_lazy('admin_review_list')

    def form_valid(self, form):
        messages.success(self.request, 'Review updated successfully.')
        return super().form_valid(form)


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = 'reviews/admin/review_confirm_delete.html'
    success_url = reverse_lazy('admin_review_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Review deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Quick action views
@login_required
def approve_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.is_approved = True
    review.save()
    messages.success(request, 'Review approved successfully.')
    return redirect('admin_review_list')


@login_required
def unapprove_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.is_approved = False
    review.save()
    messages.success(request, 'Review unapproved successfully.')
    return redirect('admin_review_list')


@login_required
def feature_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.is_featured = True
    review.save()
    messages.success(request, 'Review featured successfully.')
    return redirect('admin_review_list')


@login_required
def unfeature_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.is_featured = False
    review.save()
    messages.success(request, 'Review unfeatured successfully.')
    return redirect('admin_review_list')


# AJAX view for quick actions
@login_required
def toggle_review_status(request, pk):
    if request.method == 'POST' and request.is_ajax():
        review = get_object_or_404(Review, pk=pk)
        field = request.POST.get('field')

        if field == 'is_approved':
            review.is_approved = not review.is_approved
            status = 'approved' if review.is_approved else 'pending'
        elif field == 'is_featured':
            review.is_featured = not review.is_featured
            status = 'featured' if review.is_featured else 'not featured'
        else:
            return JsonResponse({'success': False, 'error': 'Invalid field'})

        review.save()
        return JsonResponse({'success': True, 'status': status})

    return JsonResponse({'success': False, 'error': 'Invalid request'})
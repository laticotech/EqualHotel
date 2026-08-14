from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import ContactInquiry, NewsletterSubscriber
from hotel.models import Hotel
from accounts.models import User, Profile
from .forms import ContactInquiryForm, NewsletterSubscriptionForm

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# Contact Form View
def contact_view(request):
    if request.method == 'POST':
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)

            # If user is authenticated, associate with user
            if request.user.is_authenticated:
                inquiry.user = request.user

            inquiry.save()

            # Send email notification (you can implement this later)
            # send_contact_notification(inquiry)

            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact_success')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactInquiryForm()

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

    more = 'more'
    context = {
        'form': form,
        'hotel': hotel,
        'profile': profile,
        'more': more,
        'contact': 'active',
    }
    return render(request, 'contact.html', context)


# Contact Success Page
def contact_success(request):
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
    more = 'more'
    context = {
        'hotel': hotel,
        'profile': profile,
        'more': more,
    }
    return render(request, 'contact_success.html', context)


# location
def location_view(request):
    """
    Display hotel location page
    """
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
    more = 'more'
    context = {
        'hotel': hotel,
        'profile': profile,
        'more': more,
        'location': 'active',  # for active navigation highlighting
    }
    return render(request, 'location.html', context)


# Newsletter Subscription View
@require_POST
@csrf_exempt
def newsletter_subscribe(request):
    email = request.POST.get('email')

    if email:
        try:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'is_active': True}
            )

            if not created:
                if not subscriber.is_active:
                    subscriber.is_active = True
                    subscriber.save()

                    # Send welcome back email
                    send_newsletter_welcome_back_email(subscriber)

                    return JsonResponse({
                        'success': True,
                        'message': 'Successfully resubscribed to our newsletter!'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'This email is already subscribed.'
                    })
            else:
                # Send welcome email for new subscribers
                send_newsletter_welcome_email(subscriber)

                return JsonResponse({
                    'success': True,
                    'message': 'Successfully subscribed to our newsletter!'
                })

        except Exception as e:
            print(f"Error: {e}")  # For debugging
            return JsonResponse({
                'success': False,
                'message': 'An error occurred. Please try again.'
            })

    return JsonResponse({
        'success': False,
        'message': 'Please provide a valid email address.'
    })


@login_required()
def send_newsletter_welcome_email(subscriber):
    """Send welcome email to new newsletter subscribers"""
    try:
        subject = 'Welcome to Our Newsletter!'

        # HTML content for the email
        html_message = render_to_string('newsletter_welcome.html', {
            'subscriber': subscriber,
            'unsubscribe_url': f"{settings.SITE_URL}/newsletter/unsubscribe/{subscriber.email}/"
        })

        # Plain text version
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False


@login_required()
def send_newsletter_welcome_back_email(subscriber):
    """Send welcome back email to returning subscribers"""
    try:
        subject = 'Welcome Back to Our Newsletter!'

        html_message = render_to_string('newsletter_welcome_back.html', {
            'subscriber': subscriber,
            'unsubscribe_url': f"{settings.SITE_URL}/newsletter/unsubscribe/{subscriber.email}/"
        })

        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True
    except Exception as e:
        print(f"Error sending welcome back email: {e}")
        return False


# Newsletter Unsubscribe View
def newsletter_unsubscribe(request, email):
    try:
        subscriber = NewsletterSubscriber.objects.get(email=email)
        subscriber.is_active = False
        subscriber.save()
        messages.success(request, 'You have been unsubscribed from our newsletter.')
    except NewsletterSubscriber.DoesNotExist:
        messages.error(request, 'Email address not found.')

    return redirect('home')


# Admin Views for Contact Inquiries (Require Login)
class ContactInquiryListView(LoginRequiredMixin, ListView):
    model = ContactInquiry
    template_name = 'contact/admin/inquiry_list.html'
    context_object_name = 'inquiries'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by status if provided
        status = self.request.GET.get('status')
        if status == 'resolved':
            queryset = queryset.filter(is_resolved=True)
        elif status == 'unresolved':
            queryset = queryset.filter(is_resolved=False)

        # Filter by type if provided
        inquiry_type = self.request.GET.get('type')
        if inquiry_type:
            queryset = queryset.filter(inquiry_type=inquiry_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_inquiries'] = ContactInquiry.objects.count()
        context['resolved_inquiries'] = ContactInquiry.objects.filter(is_resolved=True).count()
        context['unresolved_inquiries'] = ContactInquiry.objects.filter(is_resolved=False).count()
        return context


class ContactInquiryDetailView(LoginRequiredMixin, UpdateView):
    model = ContactInquiry
    template_name = 'contact/admin/inquiry_detail.html'
    fields = ['is_resolved', 'resolved_notes']
    success_url = reverse_lazy('contact_inquiry_list')

    def form_valid(self, form):
        messages.success(self.request, 'Inquiry updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inquiry'] = self.get_object()
        return context


class ContactInquiryDeleteView(LoginRequiredMixin, DeleteView):
    model = ContactInquiry
    template_name = 'contact/admin/inquiry_confirm_delete.html'
    success_url = reverse_lazy('contact_inquiry_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Inquiry deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Quick action views for inquiries
@require_POST
@login_required
def mark_inquiry_resolved(request, pk):
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    inquiry.is_resolved = True
    inquiry.resolved_notes = request.POST.get('resolved_notes', '')
    inquiry.save()

    messages.success(request, 'Inquiry marked as resolved.')
    return redirect('contact_inquiry_list')


@require_POST
@login_required
def mark_inquiry_unresolved(request, pk):
    inquiry = get_object_or_404(ContactInquiry, pk=pk)
    inquiry.is_resolved = False
    inquiry.resolved_notes = ''
    inquiry.save()

    messages.success(request, 'Inquiry marked as unresolved.')
    return redirect('contact_inquiry_list')


# Newsletter Subscriber Management (Admin)
class NewsletterSubscriberListView(LoginRequiredMixin, ListView):
    model = NewsletterSubscriber
    template_name = 'contact/admin/newsletter_list.html'
    context_object_name = 'subscribers'
    paginate_by = 20
    ordering = ['-subscribed_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by status if provided
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_subscribers'] = NewsletterSubscriber.objects.count()
        context['active_subscribers'] = NewsletterSubscriber.objects.filter(is_active=True).count()
        context['inactive_subscribers'] = NewsletterSubscriber.objects.filter(is_active=False).count()
        return context


@require_POST
@login_required
def toggle_subscriber_status(request, pk):
    subscriber = get_object_or_404(NewsletterSubscriber, pk=pk)
    subscriber.is_active = not subscriber.is_active
    subscriber.save()

    status = "activated" if subscriber.is_active else "deactivated"
    messages.success(request, f'Subscriber {status} successfully.')
    return redirect('newsletter_subscriber_list')


class NewsletterSubscriberDeleteView(LoginRequiredMixin, DeleteView):
    model = NewsletterSubscriber
    template_name = 'contact/admin/subscriber_confirm_delete.html'
    success_url = reverse_lazy('newsletter_subscriber_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Subscriber deleted successfully.')
        return super().delete(request, *args, **kwargs)


# Dashboard statistics
@login_required
def contact_dashboard(request):
    total_inquiries = ContactInquiry.objects.count()
    resolved_inquiries = ContactInquiry.objects.filter(is_resolved=True).count()
    unresolved_inquiries = ContactInquiry.objects.filter(is_resolved=False).count()

    total_subscribers = NewsletterSubscriber.objects.count()
    active_subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()

    # Recent inquiries
    recent_inquiries = ContactInquiry.objects.all().order_by('-created_at')[:5]

    # Inquiry type distribution
    inquiry_types = {}
    for choice in ContactInquiry.INQUIRY_TYPES:
        count = ContactInquiry.objects.filter(inquiry_type=choice[0]).count()
        inquiry_types[choice[1]] = count

    context = {
        'total_inquiries': total_inquiries,
        'resolved_inquiries': resolved_inquiries,
        'unresolved_inquiries': unresolved_inquiries,
        'total_subscribers': total_subscribers,
        'active_subscribers': active_subscribers,
        'recent_inquiries': recent_inquiries,
        'inquiry_types': inquiry_types,
    }

    return render(request, 'contact/admin/dashboard.html', context)
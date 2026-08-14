"""
URL configuration for eHospitality project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from hotel import views
from accounts import views as AccountViews
from rooms import views as RoomViews
from bookings import views as BookingViews
from gallery import views as GalleryViews
from reviews import views as ReviewViews
from contacts import views as ContactViews
from services import views as ServiceViews
from blog import views as BlogViews


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('hotel.urls')),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls')),
    path('bookings/', include('bookings.urls')),
    path('contacts/', include('contacts.urls')),
    path('gallery/', include('gallery.urls')),
    path('reviews/', include('reviews.urls')),
    path('rooms/', include('rooms.urls')),
    path('services/', include('services.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    # HOME
    path('amenities/', views.all_amenities, name='all_amenities'),
    path('about/', views.about_us, name='about_us'),
    # Public URLs
    path('events/', views.events_list, name='events_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    # Add to your existing urlpatterns
    path('events/<int:event_id>/register/', views.register_for_event, name='register_for_event'),
    path('registration/success/<int:registration_id>/', views.registration_success, name='registration_success'),
    path('my-registrations/', views.my_event_registrations, name='my_event_registrations'),
    path('registration/cancel/<int:registration_id>/', views.cancel_registration, name='cancel_registration'),

    # rooms
    path('accommodations', RoomViews.room_list, name='accommodations'),
    path('accommodation_details/<slug:slug>', RoomViews.room_detail, name='accommodation_details'),    # JSON API views
    path('api/availability/', RoomViews.room_availability_json, name='room_availability_json'),
    path('api/search/', RoomViews.room_search_json, name='room_search_json'),

    # services
    path('services/', ServiceViews.service_list, name='service_list'),
    path('services/<int:service_id>/', ServiceViews.service_detail, name='service_detail'),
    path('services/<int:service_id>/reserve/', ServiceViews.service_reservation, name='service_reservation'),
    path('service-reservation-success/<int:reservation_id>/', ServiceViews.service_reservation_success, name='service_reservation_success'),

    # gallery
    path('gallery_list/', GalleryViews.gallery_list, name='gallery_list'),
    path('featured/', GalleryViews.gallery_featured, name='gallery_featured'),
    path('search/', GalleryViews.gallery_search, name='gallery_search'),
    path('category/<int:category_id>/', GalleryViews.gallery_category, name='gallery_category'),
    path('image/<int:image_id>/', GalleryViews.gallery_image_detail, name='gallery_detail'),

    # Contact
    # Public views
    path('contact', ContactViews.contact_view, name='contact'),
    path('success/', ContactViews.contact_success, name='contact_success'),
    path('location/', ContactViews.location_view, name='location'),
    path('newsletter/subscribe/', ContactViews.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/unsubscribe/<str:email>/', ContactViews.newsletter_unsubscribe, name='newsletter_unsubscribe'),

    # Admin views (protected)
    path('admin/inquiries/', ContactViews.ContactInquiryListView.as_view(), name='contact_inquiry_list'),
    path('admin/inquiries/<int:pk>/', ContactViews.ContactInquiryDetailView.as_view(), name='contact_inquiry_detail'),
    path('admin/inquiries/<int:pk>/delete/', ContactViews.ContactInquiryDeleteView.as_view(), name='contact_inquiry_delete'),
    path('admin/inquiries/<int:pk>/resolve/', ContactViews.mark_inquiry_resolved, name='mark_inquiry_resolved'),
    path('admin/inquiries/<int:pk>/unresolve/', ContactViews.mark_inquiry_unresolved, name='mark_inquiry_unresolved'),

    path('admin/newsletter/', ContactViews.NewsletterSubscriberListView.as_view(), name='newsletter_subscriber_list'),
    path('admin/newsletter/<int:pk>/toggle/', ContactViews.toggle_subscriber_status, name='toggle_subscriber_status'),
    path('admin/newsletter/<int:pk>/delete/', ContactViews.NewsletterSubscriberDeleteView.as_view(),
         name='newsletter_subscriber_delete'),
    path('admin/dashboard/', ContactViews.contact_dashboard, name='contact_dashboard'),

    # Reviews
    # Public URLs
    path('reviews_list', ReviewViews.reviews_list, name='reviews_list'),
    path('submit/', ReviewViews.submit_review, name='submit_review'),

    # Admin URLs
    path('admin/', ReviewViews.ReviewListView.as_view(), name='admin_review_list'),
    path('admin/<int:pk>/edit/', ReviewViews.ReviewUpdateView.as_view(), name='admin_review_edit'),
    path('admin/<int:pk>/delete/', ReviewViews.ReviewDeleteView.as_view(), name='admin_review_delete'),
    path('admin/<int:pk>/approve/', ReviewViews.approve_review, name='approve_review'),
    path('admin/<int:pk>/unapprove/', ReviewViews.unapprove_review, name='unapprove_review'),
    path('admin/<int:pk>/feature/', ReviewViews.feature_review, name='feature_review'),
    path('admin/<int:pk>/unfeature/', ReviewViews.unfeature_review, name='unfeature_review'),
    path('admin/<int:pk>/toggle-status/', ReviewViews.toggle_review_status, name='toggle_review_status'),

    # Authentication URLs
    path('signup/', AccountViews.signup_view, name='signup'),
    path('login/', AccountViews.login_view, name='login'),
    path('logout/', AccountViews.logout_view, name='logout'),
    path('profile/', AccountViews.profile_view, name='profile'),

    # blog
    path('blog/', BlogViews.blog_list, name='blog_list'),
    path('category/<slug:slug>/', BlogViews.blog_category, name='blog_category'),
    path('<slug:slug>/', BlogViews.blog_detail, name='blog_detail'),



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
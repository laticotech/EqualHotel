from django.urls import path
from . import views

urlpatterns = [
    path('my_bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<str:booking_reference>/', views.booking_detail, name='booking_detail'),
    path('booking/<str:booking_reference>/cancel/', views.cancel_booking, name='cancel_booking'),

    # Service Reservations URLs
    path('my_reservations/', views.my_reservations, name='my_reservations'),
    path('reservation/<str:reservation_number>/', views.reservation_detail, name='reservation_detail'),
    path('reservation/<str:reservation_number>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('reservation/create/', views.create_reservation, name='create_reservation'),

    # Notifications URLs
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/read/<str:notification_type>/<int:item_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/clear/', views.clear_all_notifications, name='clear_all_notifications'),

    # Admin Dashboard
    path('admin/dashboard/', views.admin_dashboard, name='dashboard'),

    # Bookings Management
    path('admin/bookings/', views.admin_bookings, name='admin_bookings'),
    path('admin/bookings/<int:booking_id>/', views.admin_booking_detail, name='admin_booking_detail'),

    # Service Reservations Management
    path('admin/reservations/', views.admin_reservations, name='admin_reservations'),
    path('admin/reservations/<int:reservation_id>/', views.admin_reservation_detail, name='admin_reservation_detail'),

    # Contact Messages Management
    path('admin/messages/', views.admin_messages, name='admin_messages'),
    path('admin/messages/<int:message_id>/', views.admin_message_detail, name='admin_message_detail'),

    # Payments Management
    path('admin/payments/', views.admin_payments, name='admin_payments'),

    # Blog Management
    path('admin/blog/', views.admin_blog, name='admin_blog'),
    path('admin/blog/create/', views.admin_blog_create, name='admin_blog_create'),
    path('admin/blog/<int:post_id>/edit/', views.admin_blog_edit, name='admin_blog_edit'),

    # Team Management
    path('admin/team/', views.admin_team, name='admin_team'),
    path('admin/team/create/', views.admin_team_create, name='admin_team_create'),
    path('admin/team/<int:member_id>/edit/', views.admin_team_edit, name='admin_team_edit'),

    # Reports
    path('admin/reports/', views.admin_reports, name='admin_reports'),

    # Notifications
    path('admin/dashboard/', views.admin_dashboard, name='dashboard'),
    path('admin/notifications/counts/', views.get_admin_notification_counts, name='notification_counts'),
    path('admin/notifications/recent/', views.get_recent_notifications, name='recent_notifications'),

    # Booking Payments
    path('admin/bookings/', views.booking_payments_list, name='admin_booking_payments'),
    path('admin/bookings/receive/<str:booking_reference>/', views.receive_booking_payment,
         name='receive_booking_payment'),
    path('admin/bookings/edit/<int:payment_id>/', views.edit_booking_payment, name='edit_booking_payment'),

    # Service Reservation Payments
    path('admin/services/', views.service_payments_list, name='admin_service_payments'),
    path('admin/services/receive/<str:reservation_number>/', views.receive_service_payment,
         name='receive_service_payment'),
    path('admin/services/edit/<int:payment_id>/', views.edit_service_payment, name='edit_service_payment'),

    # Admin Events URLs
    path('admin/events/', views.admin_events, name='admin_events'),
    path('admin/events/create/', views.create_event, name='create_event'),
    path('admin/events/edit/<int:event_id>/', views.edit_event, name='edit_event'),
    path('admin/events/delete/<int:event_id>/', views.delete_event, name='delete_event'),

]
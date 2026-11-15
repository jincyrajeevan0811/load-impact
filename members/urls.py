from django.urls import path

from . import views

app_name = "members"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("subscribe/<int:plan_id>/", views.subscribe, name="subscribe"),
    path("classes/", views.classes, name="classes"),
    path("classes/<int:class_id>/book/", views.book_class, name="book_class"),
    path("bookings/", views.bookings, name="bookings"),
    path("bookings/<int:pk>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("billing/", views.billing, name="billing"),
    path("invoice/<int:pk>/", views.invoice, name="invoice"),
    path("attendance/", views.attendance, name="attendance"),
]

from django.urls import path

from appearance import views as appearance_views

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),

    # Members
    path("members/", views.member_list, name="member_list"),
    path("members/add/", views.member_add, name="member_add"),
    path("members/<int:pk>/", views.member_detail, name="member_detail"),
    path("members/<int:pk>/edit/", views.member_edit, name="member_edit"),
    path("members/<int:pk>/toggle/", views.member_toggle, name="member_toggle"),
    path("members/<int:pk>/delete/", views.member_delete, name="member_delete"),
    path("members/<int:pk>/password/", views.member_password, name="member_password"),
    path("members/<int:pk>/checkin/", views.member_checkin, name="member_checkin"),

    # Plans
    path("plans/", views.PlanList.as_view(), name="plan_list"),
    path("plans/add/", views.PlanCreate.as_view(), name="plan_add"),
    path("plans/<int:pk>/edit/", views.PlanUpdate.as_view(), name="plan_edit"),
    path("plans/<int:pk>/delete/", views.PlanDelete.as_view(), name="plan_delete"),

    # Trainers
    path("trainers/", views.TrainerList.as_view(), name="trainer_list"),
    path("trainers/add/", views.TrainerCreate.as_view(), name="trainer_add"),
    path("trainers/<int:pk>/edit/", views.TrainerUpdate.as_view(), name="trainer_edit"),
    path("trainers/<int:pk>/delete/", views.TrainerDelete.as_view(), name="trainer_delete"),

    # Classes
    path("classes/", views.ClassList.as_view(), name="class_list"),
    path("classes/add/", views.ClassCreate.as_view(), name="class_add"),
    path("classes/<int:pk>/edit/", views.ClassUpdate.as_view(), name="class_edit"),
    path("classes/<int:pk>/delete/", views.ClassDelete.as_view(), name="class_delete"),

    # Memberships
    path("memberships/", views.membership_list, name="membership_list"),
    path("memberships/add/", views.membership_add, name="membership_add"),
    path("memberships/<int:pk>/edit/", views.membership_edit, name="membership_edit"),
    path("memberships/<int:pk>/activate/", views.membership_activate, name="membership_activate"),
    path("memberships/<int:pk>/cancel/", views.membership_cancel, name="membership_cancel"),
    path("memberships/<int:pk>/delete/", views.MembershipDelete.as_view(), name="membership_delete"),

    # Payments
    path("payments/", views.payment_list, name="payment_list"),
    path("payments/add/", views.PaymentCreate.as_view(), name="payment_add"),
    path("payments/<int:pk>/edit/", views.PaymentUpdate.as_view(), name="payment_edit"),
    path("payments/<int:pk>/paid/", views.payment_mark_paid, name="payment_paid"),
    path("payments/<int:pk>/delete/", views.PaymentDelete.as_view(), name="payment_delete"),

    # Bookings
    path("bookings/", views.booking_list, name="booking_list"),
    path("bookings/<int:pk>/status/<str:status>/", views.booking_status, name="booking_status"),

    # Attendance
    path("attendance/", views.attendance_list, name="attendance_list"),
    path("attendance/<int:pk>/checkout/", views.attendance_checkout, name="attendance_checkout"),
    path("attendance/<int:pk>/edit/", views.AttendanceUpdate.as_view(), name="attendance_edit"),
    path("attendance/<int:pk>/delete/", views.AttendanceDelete.as_view(), name="attendance_delete"),

    # Messages
    path("messages/", views.message_list, name="message_list"),
    path("messages/<int:pk>/", views.message_detail, name="message_detail"),
    path("messages/<int:pk>/toggle/", views.message_toggle, name="message_toggle"),
    path("messages/<int:pk>/delete/", views.MessageDelete.as_view(), name="message_delete"),

    # Announcements
    path("announcements/", views.AnnouncementList.as_view(), name="announcement_list"),
    path("announcements/add/", views.AnnouncementCreate.as_view(), name="announcement_add"),
    path("announcements/<int:pk>/edit/", views.AnnouncementUpdate.as_view(), name="announcement_edit"),
    path("announcements/<int:pk>/delete/", views.AnnouncementDelete.as_view(), name="announcement_delete"),

    # Reports
    path("reports/", views.reports, name="reports"),

    # Appearance (website & dashboard look, page content, navigation)
    path("appearance/", appearance_views.appearance_home, name="appearance_home"),
    path("appearance/branding/", appearance_views.appearance_branding, name="appearance_branding"),
    path("appearance/colors/", appearance_views.appearance_colors, name="appearance_colors"),
    path("appearance/contact/", appearance_views.appearance_contact, name="appearance_contact"),
    path("appearance/pages/", appearance_views.appearance_pages, name="appearance_pages"),
    path("appearance/sections/<int:pk>/", appearance_views.appearance_section_edit, name="appearance_section_edit"),
    path("appearance/sections/<int:pk>/toggle/", appearance_views.appearance_section_toggle, name="appearance_section_toggle"),
    path("appearance/sections/<int:pk>/move/<str:direction>/", appearance_views.appearance_section_move, name="appearance_section_move"),
    path("appearance/sections/<int:pk>/reset/", appearance_views.appearance_section_reset, name="appearance_section_reset"),
    path("appearance/navigation/", appearance_views.appearance_nav, name="appearance_nav"),
    path("appearance/navigation/<int:pk>/edit/", appearance_views.appearance_nav_edit, name="appearance_nav_edit"),
    path("appearance/navigation/<int:pk>/<str:action>/", appearance_views.appearance_nav_action, name="appearance_nav_action"),
]

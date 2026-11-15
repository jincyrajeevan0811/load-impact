from django.contrib import admin

from .models import (
    Announcement,
    Attendance,
    Booking,
    ContactMessage,
    GymClass,
    Membership,
    MembershipPlan,
    Payment,
    Trainer,
)


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "duration_days", "price", "is_popular", "is_active")
    list_editable = ("is_popular", "is_active")


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ("name", "gender", "specialization", "experience_years", "is_active")
    list_filter = ("gender", "is_active")
    search_fields = ("name", "specialization")


@admin.register(GymClass)
class GymClassAdmin(admin.ModelAdmin):
    list_display = ("name", "trainer", "day_of_week", "start_time", "end_time", "capacity", "is_active")
    list_filter = ("day_of_week", "level", "is_active")


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "start_date", "end_date", "status")
    list_filter = ("status", "plan")
    search_fields = ("user__username", "user__email")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice_no", "user", "amount", "method", "status", "paid_at", "created_at")
    list_filter = ("status", "method")
    search_fields = ("user__username", "transaction_id")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "gym_class", "date", "status")
    list_filter = ("status", "date")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "check_in", "check_out")
    list_filter = ("date",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "is_read", "created_at")
    list_filter = ("is_read",)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")

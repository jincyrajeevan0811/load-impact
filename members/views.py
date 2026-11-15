from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from gym.models import (
    DAY_CHOICES,
    Announcement,
    Booking,
    GymClass,
    Membership,
    MembershipPlan,
    Payment,
)

from .forms import SubscribeForm


@login_required
def dashboard(request):
    Membership.expire_old()
    user = request.user
    today = timezone.localdate()
    current = Membership.current_for(user)
    context = {
        "current": current,
        "upcoming_membership": user.memberships.filter(status="active", start_date__gt=today)
        .select_related("plan")
        .first(),
        "pending": user.memberships.filter(status="pending").select_related("plan").first(),
        "upcoming_bookings": user.bookings.filter(date__gte=today, status="booked")
        .select_related("gym_class", "gym_class__trainer")
        .order_by("date", "gym_class__start_time")[:5],
        "recent_attendance": user.attendances.all()[:5],
        "visits_this_month": user.attendances.filter(
            date__year=today.year, date__month=today.month
        ).count(),
        "classes_attended": user.bookings.filter(status="attended").count(),
        "total_spent": user.payments.filter(status="paid").aggregate(total=Sum("amount"))["total"] or 0,
        "announcements": Announcement.objects.filter(is_active=True)[:4],
        "plans": MembershipPlan.objects.filter(is_active=True) if not current else None,
    }
    return render(request, "members/dashboard.html", context)


@login_required
def subscribe(request, plan_id):
    plan = get_object_or_404(MembershipPlan, pk=plan_id, is_active=True)
    if request.user.memberships.filter(status="pending").exists():
        messages.warning(
            request,
            "You already have a membership request waiting for approval. "
            "Please wait for the front desk to confirm it.",
        )
        return redirect("members:dashboard")

    if request.method == "POST":
        form = SubscribeForm(request.POST)
        if form.is_valid():
            membership = Membership.objects.create(
                user=request.user, plan=plan, status="pending", notes=form.cleaned_data["notes"]
            )
            Payment.objects.create(
                user=request.user,
                membership=membership,
                amount=plan.price,
                method=form.cleaned_data["method"],
                transaction_id=form.cleaned_data["transaction_id"],
                notes=form.cleaned_data["notes"],
                status="pending",
            )
            messages.success(
                request,
                f"Your request for the {plan.name} plan has been submitted. "
                "It will be activated once the payment is confirmed by the gym.",
            )
            return redirect("members:billing")
    else:
        form = SubscribeForm()
    return render(
        request,
        "members/subscribe.html",
        {"plan": plan, "form": form, "current": Membership.current_for(request.user)},
    )


@login_required
def classes(request):
    current = Membership.current_for(request.user)
    all_classes = GymClass.objects.filter(is_active=True).select_related("trainer")
    my_booked = set(
        request.user.bookings.filter(date__gte=timezone.localdate(), status="booked").values_list(
            "gym_class_id", "date"
        )
    )
    week = []
    for day_num, day_name in DAY_CHOICES:
        day_classes = []
        for c in all_classes:
            if c.day_of_week != day_num:
                continue
            next_date = c.next_date()
            day_classes.append(
                {
                    "obj": c,
                    "next_date": next_date,
                    "seats_left": c.seats_left(next_date),
                    "is_booked": (c.id, next_date) in my_booked,
                }
            )
        week.append({"day": day_name, "classes": day_classes})
    return render(request, "members/classes.html", {"week": week, "current": current})


@login_required
@require_POST
def book_class(request, class_id):
    gym_class = get_object_or_404(GymClass, pk=class_id, is_active=True)
    if not Membership.current_for(request.user):
        messages.error(request, "You need an active membership to book classes.")
        return redirect("members:classes")

    date = gym_class.next_date()
    booking = Booking.objects.filter(user=request.user, gym_class=gym_class, date=date).first()
    if booking and booking.status != "cancelled":
        messages.info(request, f"You have already booked {gym_class.name} on {date:%d %b}.")
        return redirect("members:classes")
    if gym_class.seats_left(date) <= 0:
        messages.error(request, f"Sorry, {gym_class.name} on {date:%d %b} is fully booked.")
        return redirect("members:classes")

    if booking:
        booking.status = "booked"
        booking.save()
    else:
        Booking.objects.create(user=request.user, gym_class=gym_class, date=date)
    messages.success(
        request,
        f"Booked! {gym_class.name} on {date:%A, %d %b} at {gym_class.start_time:%I:%M %p}.",
    )
    return redirect("members:bookings")


@login_required
def bookings(request):
    today = timezone.localdate()
    qs = request.user.bookings.select_related("gym_class", "gym_class__trainer")
    return render(
        request,
        "members/bookings.html",
        {
            "upcoming": qs.filter(date__gte=today).order_by("date", "gym_class__start_time"),
            "past": qs.filter(date__lt=today)[:30],
        },
    )


@login_required
@require_POST
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.can_cancel:
        booking.status = "cancelled"
        booking.save()
        messages.success(request, f"Your booking for {booking.gym_class.name} was cancelled.")
    else:
        messages.error(request, "This booking can no longer be cancelled.")
    return redirect("members:bookings")


@login_required
def billing(request):
    Membership.expire_old()
    return render(
        request,
        "members/billing.html",
        {
            "memberships": request.user.memberships.select_related("plan"),
            "payments": request.user.payments.select_related("membership__plan"),
        },
    )


@login_required
def invoice(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if payment.user != request.user and not request.user.is_staff:
        messages.error(request, "You cannot view this invoice.")
        return redirect("members:billing")
    return render(request, "members/invoice.html", {"payment": payment})


@login_required
def attendance(request):
    records = request.user.attendances.all()[:60]
    today = timezone.localdate()
    return render(
        request,
        "members/attendance.html",
        {
            "records": records,
            "this_month": request.user.attendances.filter(
                date__year=today.year, date__month=today.month
            ).count(),
            "total": request.user.attendances.count(),
        },
    )

import csv
from datetime import datetime, timedelta
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, ProtectedError, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.forms import BootstrapFormMixin, ProfileForm
from accounts.models import Profile
from gym.models import (
    DAY_CHOICES,
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

from .forms import (
    AnnouncementForm,
    CheckInForm,
    GymClassForm,
    MemberCreateForm,
    MembershipForm,
    MemberUpdateForm,
    PaymentForm,
    PlanForm,
    TrainerForm,
)

User = get_user_model()


# =====================================================================
# Access control
# =====================================================================
def staff_required(view_func):
    """Only logged-in staff users may access the admin dashboard."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class DashFormMixin(StaffRequiredMixin, SuccessMessageMixin):
    """Shared behaviour for dashboard create / update views."""

    template_name = "dashboard/form.html"
    page_title = ""
    list_url_name = ""

    def get_success_url(self):
        return reverse(self.list_url_name)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["page_title"] = self.page_title
        ctx["back_url"] = reverse(self.list_url_name)
        return ctx


class DashDeleteView(StaffRequiredMixin, DeleteView):
    template_name = "dashboard/confirm_delete.html"
    list_url_name = ""

    def get_success_url(self):
        return reverse(self.list_url_name)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["back_url"] = reverse(self.list_url_name)
        return ctx

    def form_valid(self, form):
        label = str(self.object)
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f'"{label}" cannot be deleted because other records depend on it. '
                "Deactivate it instead.",
            )
            return redirect(self.get_success_url())
        messages.success(self.request, f'"{label}" was deleted.')
        return response


def _get_date(request, key, default=None):
    """Read a YYYY-MM-DD query parameter safely (invalid values are ignored)."""
    try:
        value = parse_date(request.GET.get(key, "") or "")
    except ValueError:
        value = None
    return value or default


def _paginate(request, qs, per_page=15):
    return Paginator(qs, per_page).get_page(request.GET.get("page"))


def _csv_response(filename, header, rows):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return response


def _last_n_months(n=6):
    today = timezone.localdate()
    year, month = today.year, today.month
    months = []
    for _ in range(n):
        months.append((year, month))
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    return list(reversed(months))


def _active_membership_user_ids():
    today = timezone.localdate()
    return Membership.objects.filter(
        status="active", start_date__lte=today, end_date__gte=today
    ).values_list("user_id", flat=True)


# =====================================================================
# Dashboard home
# =====================================================================
@staff_required
def home(request):
    Membership.expire_old()
    today = timezone.localdate()
    members = User.objects.filter(is_staff=False)
    active_ms = Membership.objects.filter(status="active", start_date__lte=today, end_date__gte=today)
    paid = Payment.objects.filter(status="paid")

    stats = {
        "total_members": members.count(),
        "active_members": active_ms.values("user").distinct().count(),
        "new_members_month": members.filter(
            date_joined__year=today.year, date_joined__month=today.month
        ).count(),
        "revenue_month": paid.filter(paid_at__year=today.year, paid_at__month=today.month).aggregate(
            s=Sum("amount")
        )["s"] or 0,
        "revenue_total": paid.aggregate(s=Sum("amount"))["s"] or 0,
        "pending_payments": Payment.objects.filter(status="pending").count(),
        "pending_amount": Payment.objects.filter(status="pending").aggregate(s=Sum("amount"))["s"] or 0,
        "checkins_today": Attendance.objects.filter(date=today).count(),
        "in_gym_now": Attendance.objects.filter(date=today, check_out__isnull=True).count(),
        "unread_messages": ContactMessage.objects.filter(is_read=False).count(),
        "trainers": Trainer.objects.filter(is_active=True).count(),
        "classes": GymClass.objects.filter(is_active=True).count(),
    }

    # Charts
    labels, revenue, signups = [], [], []
    for year, month in _last_n_months(6):
        labels.append(datetime(year, month, 1).strftime("%b %Y"))
        revenue.append(
            float(
                paid.filter(paid_at__year=year, paid_at__month=month).aggregate(s=Sum("amount"))["s"] or 0
            )
        )
        signups.append(members.filter(date_joined__year=year, date_joined__month=month).count())

    gender_map = dict(Profile.GENDER_CHOICES)
    gender_rows = (
        Profile.objects.filter(user__is_staff=False).values("gender").annotate(c=Count("id")).order_by("gender")
    )
    plan_rows = active_ms.values("plan__name").annotate(c=Count("id")).order_by("-c")

    chart_data = {
        "labels": labels,
        "revenue": revenue,
        "signups": signups,
        "gender_labels": [gender_map.get(r["gender"], "Not set") for r in gender_rows],
        "gender_values": [r["c"] for r in gender_rows],
        "plan_labels": [r["plan__name"] for r in plan_rows],
        "plan_values": [r["c"] for r in plan_rows],
    }

    todays_classes = [
        {"obj": c, "booked": c.booked_count(today)}
        for c in GymClass.objects.filter(is_active=True, day_of_week=today.weekday()).select_related("trainer")
    ]

    context = {
        "stats": stats,
        "chart_data": chart_data,
        "todays_classes": todays_classes,
        "expiring": active_ms.filter(end_date__lte=today + timedelta(days=7))
        .select_related("user", "plan")
        .order_by("end_date")[:8],
        "pending_memberships": Membership.objects.filter(status="pending").select_related("user", "plan")[:6],
        "recent_payments": Payment.objects.select_related("user", "membership__plan")[:6],
        "recent_members": members.select_related("profile").order_by("-date_joined")[:6],
        "today": today,
    }
    return render(request, "dashboard/home.html", context)


# =====================================================================
# Members
# =====================================================================
@staff_required
def member_list(request):
    Membership.expire_old()
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    role = request.GET.get("role", "members")

    qs = User.objects.select_related("profile").order_by("-date_joined")
    qs = qs.filter(is_staff=True) if role == "staff" else qs.filter(is_staff=False)
    if q:
        qs = qs.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(email__icontains=q)
            | Q(profile__phone__icontains=q)
        )
    active_ids = set(_active_membership_user_ids())
    if status == "active":
        qs = qs.filter(id__in=active_ids)
    elif status == "inactive":
        qs = qs.exclude(id__in=active_ids)
    elif status == "disabled":
        qs = qs.filter(is_active=False)

    if request.GET.get("export") == "csv":
        rows = []
        for u in qs:
            p = getattr(u, "profile", None)
            rows.append([
                p.member_id if p else "", u.username, u.get_full_name(), u.email,
                p.phone if p else "", p.get_gender_display() if p else "",
                "Yes" if u.id in active_ids else "No", u.date_joined.strftime("%Y-%m-%d"),
            ])
        return _csv_response(
            "loadimpact_members.csv",
            ["Member ID", "Username", "Name", "Email", "Phone", "Gender", "Active Plan", "Joined"],
            rows,
        )

    return render(
        request,
        "dashboard/members.html",
        {
            "page_obj": _paginate(request, qs),
            "q": q,
            "status": status,
            "role": role,
            "active_ids": active_ids,
        },
    )


@staff_required
def member_add(request):
    if request.method == "POST":
        user_form = MemberCreateForm(request.POST)
        profile_form = ProfileForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            ProfileForm(request.POST, request.FILES, instance=profile).save()
            messages.success(request, f"Member {user.get_full_name() or user.username} created.")
            return redirect("dashboard:member_detail", pk=user.pk)
    else:
        user_form = MemberCreateForm()
        profile_form = ProfileForm()
    return render(
        request,
        "dashboard/member_form.html",
        {"user_form": user_form, "profile_form": profile_form, "page_title": "Add Member"},
    )


def _check_can_manage(request, target):
    if target.is_superuser and not request.user.is_superuser:
        raise PermissionDenied("Only a superuser can modify another superuser.")


@staff_required
def member_detail(request, pk):
    Membership.expire_old()
    Profile.objects.get_or_create(user_id=get_object_or_404(User, pk=pk).pk)
    member = User.objects.select_related("profile").get(pk=pk)
    today = timezone.localdate()
    context = {
        "member": member,
        "current": Membership.current_for(member),
        "memberships": member.memberships.select_related("plan"),
        "payments": member.payments.select_related("membership__plan")[:10],
        "bookings": member.bookings.select_related("gym_class")[:10],
        "attendance": member.attendances.all()[:10],
        "visits_month": member.attendances.filter(date__year=today.year, date__month=today.month).count(),
        "total_paid": member.payments.filter(status="paid").aggregate(s=Sum("amount"))["s"] or 0,
        "checked_in_today": member.attendances.filter(date=today, check_out__isnull=True).first(),
    }
    return render(request, "dashboard/member_detail.html", context)


@staff_required
def member_edit(request, pk):
    member = get_object_or_404(User, pk=pk)
    _check_can_manage(request, member)
    profile, _ = Profile.objects.get_or_create(user=member)
    if request.method == "POST":
        user_form = MemberUpdateForm(request.POST, instance=member, editor=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            if member == request.user and not user_form.cleaned_data.get("is_active", True):
                messages.error(request, "You cannot deactivate your own account.")
            else:
                user_form.save()
                profile_form.save()
                messages.success(request, "Member details updated.")
                return redirect("dashboard:member_detail", pk=member.pk)
    else:
        user_form = MemberUpdateForm(instance=member, editor=request.user)
        profile_form = ProfileForm(instance=profile)
    return render(
        request,
        "dashboard/member_form.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "member": member,
            "page_title": f"Edit {member.get_full_name() or member.username}",
        },
    )


@staff_required
@require_POST
def member_toggle(request, pk):
    member = get_object_or_404(User, pk=pk)
    _check_can_manage(request, member)
    if member == request.user:
        messages.error(request, "You cannot deactivate your own account.")
    else:
        member.is_active = not member.is_active
        member.save(update_fields=["is_active"])
        messages.success(
            request, f"Account {'enabled' if member.is_active else 'disabled'} for {member.username}."
        )
    return redirect("dashboard:member_detail", pk=pk)


@staff_required
def member_delete(request, pk):
    member = get_object_or_404(User, pk=pk)
    _check_can_manage(request, member)
    if member == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect("dashboard:member_detail", pk=pk)
    if request.method == "POST":
        name = member.get_full_name() or member.username
        member.delete()
        messages.success(request, f"Member {name} and all their records were deleted.")
        return redirect("dashboard:member_list")
    return render(
        request,
        "dashboard/confirm_delete.html",
        {
            "object": member,
            "back_url": reverse("dashboard:member_detail", args=[pk]),
            "warning": "This permanently removes the member's profile, memberships, payments, bookings and attendance.",
        },
    )


class StyledSetPasswordForm(BootstrapFormMixin, SetPasswordForm):
    pass


@staff_required
def member_password(request, pk):
    member = get_object_or_404(User, pk=pk)
    _check_can_manage(request, member)
    if request.method == "POST":
        form = StyledSetPasswordForm(member, request.POST)
        if form.is_valid():
            form.save()
            if member == request.user:
                update_session_auth_hash(request, member)
            messages.success(request, f"Password reset for {member.username}.")
            return redirect("dashboard:member_detail", pk=pk)
    else:
        form = StyledSetPasswordForm(member)
    return render(
        request,
        "dashboard/form.html",
        {
            "form": form,
            "page_title": f"Set new password for {member.username}",
            "back_url": reverse("dashboard:member_detail", args=[pk]),
        },
    )


@staff_required
@require_POST
def member_checkin(request, pk):
    member = get_object_or_404(User, pk=pk)
    now = timezone.localtime()
    open_visit = member.attendances.filter(date=now.date(), check_out__isnull=True).first()
    if open_visit:
        open_visit.check_out = now.time().replace(microsecond=0)
        open_visit.save()
        messages.success(request, f"{member.username} checked out at {now:%I:%M %p}.")
    else:
        if not Membership.current_for(member):
            messages.warning(request, f"Note: {member.username} has no active membership.")
        Attendance.objects.create(user=member, date=now.date(), check_in=now.time().replace(microsecond=0))
        messages.success(request, f"{member.username} checked in at {now:%I:%M %p}.")
    return redirect(request.POST.get("next") or reverse("dashboard:member_detail", args=[pk]))


# =====================================================================
# Membership plans
# =====================================================================
class PlanList(StaffRequiredMixin, ListView):
    template_name = "dashboard/plans.html"
    context_object_name = "plans"

    def get_queryset(self):
        today = timezone.localdate()
        return MembershipPlan.objects.annotate(
            active_count=Count(
                "memberships",
                filter=Q(memberships__status="active", memberships__end_date__gte=today),
            ),
            total_count=Count("memberships"),
        )


class PlanCreate(DashFormMixin, CreateView):
    model = MembershipPlan
    form_class = PlanForm
    page_title = "Add Membership Plan"
    list_url_name = "dashboard:plan_list"
    success_message = 'Plan "%(name)s" created.'


class PlanUpdate(DashFormMixin, UpdateView):
    model = MembershipPlan
    form_class = PlanForm
    page_title = "Edit Membership Plan"
    list_url_name = "dashboard:plan_list"
    success_message = 'Plan "%(name)s" updated.'


class PlanDelete(DashDeleteView):
    model = MembershipPlan
    list_url_name = "dashboard:plan_list"


# =====================================================================
# Trainers
# =====================================================================
class TrainerList(StaffRequiredMixin, ListView):
    template_name = "dashboard/trainers.html"
    context_object_name = "trainers"

    def get_queryset(self):
        return Trainer.objects.annotate(class_count=Count("classes", filter=Q(classes__is_active=True)))


class TrainerCreate(DashFormMixin, CreateView):
    model = Trainer
    form_class = TrainerForm
    page_title = "Add Trainer"
    list_url_name = "dashboard:trainer_list"
    success_message = 'Trainer "%(name)s" added.'


class TrainerUpdate(DashFormMixin, UpdateView):
    model = Trainer
    form_class = TrainerForm
    page_title = "Edit Trainer"
    list_url_name = "dashboard:trainer_list"
    success_message = 'Trainer "%(name)s" updated.'


class TrainerDelete(DashDeleteView):
    model = Trainer
    list_url_name = "dashboard:trainer_list"


# =====================================================================
# Classes
# =====================================================================
class ClassList(StaffRequiredMixin, ListView):
    template_name = "dashboard/classes.html"
    context_object_name = "classes"

    def get_queryset(self):
        qs = GymClass.objects.select_related("trainer")
        day = self.request.GET.get("day", "")
        if day.isdigit():
            qs = qs.filter(day_of_week=int(day))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["days"] = DAY_CHOICES
        ctx["selected_day"] = self.request.GET.get("day", "")
        return ctx


class ClassCreate(DashFormMixin, CreateView):
    model = GymClass
    form_class = GymClassForm
    page_title = "Add Class"
    list_url_name = "dashboard:class_list"
    success_message = 'Class "%(name)s" added to the schedule.'


class ClassUpdate(DashFormMixin, UpdateView):
    model = GymClass
    form_class = GymClassForm
    page_title = "Edit Class"
    list_url_name = "dashboard:class_list"
    success_message = 'Class "%(name)s" updated.'


class ClassDelete(DashDeleteView):
    model = GymClass
    list_url_name = "dashboard:class_list"


# =====================================================================
# Memberships
# =====================================================================
def _save_membership(form):
    """Save a membership from MembershipForm, filling in dates sensibly."""
    membership = form.save(commit=False)
    if membership.status == "active" and not (membership.start_date and membership.end_date):
        membership.activate(start=membership.start_date)  # computes end date & saves
    else:
        if membership.start_date and not membership.end_date:
            membership.end_date = membership.start_date + timedelta(days=membership.plan.duration_days - 1)
        membership.save()
    return membership


@staff_required
def membership_list(request):
    Membership.expire_old()
    status = request.GET.get("status", "")
    q = request.GET.get("q", "").strip()
    qs = Membership.objects.select_related("user", "plan")
    if status:
        qs = qs.filter(status=status)
    if q:
        qs = qs.filter(
            Q(user__username__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(plan__name__icontains=q)
        )
    counts = dict(Membership.objects.order_by().values_list("status").annotate(c=Count("id")))
    return render(
        request,
        "dashboard/memberships.html",
        {
            "page_obj": _paginate(request, qs),
            "status": status,
            "q": q,
            "status_choices": Membership.STATUS_CHOICES,
            "counts": counts,
        },
    )


@staff_required
def membership_add(request):
    initial = {}
    if request.GET.get("user"):
        initial["user"] = request.GET["user"]
    if request.method == "POST":
        form = MembershipForm(request.POST)
        if form.is_valid():
            membership = _save_membership(form)
            if form.cleaned_data.get("record_payment"):
                pay_status = form.cleaned_data.get("payment_status") or "paid"
                payment = Payment.objects.create(
                    user=membership.user,
                    membership=membership,
                    amount=membership.plan.price,
                    method=form.cleaned_data.get("payment_method") or "cash",
                    status=pay_status,
                    paid_at=timezone.now() if pay_status == "paid" else None,
                    notes="Recorded by staff",
                )
                if pay_status == "paid" and membership.status == "pending":
                    membership.activate()
                messages.info(request, f"Payment {payment.invoice_no} recorded.")
            messages.success(request, f"Membership created for {membership.user.username}.")
            return redirect("dashboard:membership_list")
    else:
        form = MembershipForm(initial=initial)
    return render(
        request,
        "dashboard/form.html",
        {"form": form, "page_title": "Assign Membership", "back_url": reverse("dashboard:membership_list")},
    )


@staff_required
def membership_edit(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    if request.method == "POST":
        form = MembershipForm(request.POST, instance=membership)
        if form.is_valid():
            _save_membership(form)
            messages.success(request, "Membership updated.")
            return redirect("dashboard:membership_list")
    else:
        form = MembershipForm(instance=membership)
    return render(
        request,
        "dashboard/form.html",
        {"form": form, "page_title": "Edit Membership", "back_url": reverse("dashboard:membership_list")},
    )


@staff_required
@require_POST
def membership_activate(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    membership.activate()
    updated = membership.payments.filter(status="pending").update(status="paid", paid_at=timezone.now())
    msg = f"{membership.plan.name} activated for {membership.user.username} until {membership.end_date:%d %b %Y}."
    if updated:
        msg += f" {updated} pending payment(s) marked as paid."
    messages.success(request, msg)
    return redirect(request.POST.get("next") or reverse("dashboard:membership_list"))


@staff_required
@require_POST
def membership_cancel(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    membership.status = "cancelled"
    membership.save(update_fields=["status"])
    messages.success(request, f"Membership for {membership.user.username} cancelled.")
    return redirect(request.POST.get("next") or reverse("dashboard:membership_list"))


class MembershipDelete(DashDeleteView):
    model = Membership
    list_url_name = "dashboard:membership_list"


# =====================================================================
# Payments
# =====================================================================
@staff_required
def payment_list(request):
    status = request.GET.get("status", "")
    method = request.GET.get("method", "")
    q = request.GET.get("q", "").strip()
    date_from = _get_date(request, "from")
    date_to = _get_date(request, "to")

    qs = Payment.objects.select_related("user", "membership__plan")
    if status:
        qs = qs.filter(status=status)
    if method:
        qs = qs.filter(method=method)
    if q:
        qs = qs.filter(
            Q(user__username__icontains=q)
            | Q(user__first_name__icontains=q)
            | Q(user__last_name__icontains=q)
            | Q(transaction_id__icontains=q)
        )
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    if request.GET.get("export") == "csv":
        rows = [
            [
                p.invoice_no, p.created_at.strftime("%Y-%m-%d"), p.user.username, p.user.get_full_name(),
                p.membership.plan.name if p.membership else "", p.amount, p.get_method_display(),
                p.get_status_display(), p.transaction_id,
                timezone.localtime(p.paid_at).strftime("%Y-%m-%d %H:%M") if p.paid_at else "",
            ]
            for p in qs
        ]
        return _csv_response(
            "loadimpact_payments.csv",
            ["Invoice", "Date", "Username", "Name", "Plan", "Amount", "Method", "Status", "Reference", "Paid At"],
            rows,
        )

    totals = {
        "paid": qs.filter(status="paid").aggregate(s=Sum("amount"))["s"] or 0,
        "pending": qs.filter(status="pending").aggregate(s=Sum("amount"))["s"] or 0,
    }
    return render(
        request,
        "dashboard/payments.html",
        {
            "page_obj": _paginate(request, qs),
            "status": status,
            "method": method,
            "q": q,
            "date_from": date_from.isoformat() if date_from else "",
            "date_to": date_to.isoformat() if date_to else "",
            "totals": totals,
            "status_choices": Payment.STATUS_CHOICES,
            "method_choices": Payment.METHOD_CHOICES,
        },
    )


def _after_payment_saved(payment):
    if payment.status == "paid":
        if not payment.paid_at:
            payment.paid_at = timezone.now()
            payment.save(update_fields=["paid_at"])
        if payment.membership and payment.membership.status == "pending":
            payment.membership.activate()


class PaymentCreate(DashFormMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    page_title = "Record Payment"
    list_url_name = "dashboard:payment_list"
    success_message = "Payment recorded."

    def get_initial(self):
        initial = super().get_initial()
        if self.request.GET.get("user"):
            initial["user"] = self.request.GET["user"]
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        _after_payment_saved(self.object)
        return response


class PaymentUpdate(DashFormMixin, UpdateView):
    model = Payment
    form_class = PaymentForm
    page_title = "Edit Payment"
    list_url_name = "dashboard:payment_list"
    success_message = "Payment updated."

    def form_valid(self, form):
        response = super().form_valid(form)
        _after_payment_saved(self.object)
        return response


@staff_required
@require_POST
def payment_mark_paid(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    payment.mark_paid()
    msg = f"{payment.invoice_no} marked as paid."
    if payment.membership and payment.membership.status == "active":
        msg += f" Membership active until {payment.membership.end_date:%d %b %Y}."
    messages.success(request, msg)
    return redirect(request.POST.get("next") or reverse("dashboard:payment_list"))


class PaymentDelete(DashDeleteView):
    model = Payment
    list_url_name = "dashboard:payment_list"


# =====================================================================
# Bookings
# =====================================================================
@staff_required
def booking_list(request):
    today = timezone.localdate()
    date = _get_date(request, "date")
    status = request.GET.get("status", "")
    class_id = request.GET.get("class", "")

    qs = Booking.objects.select_related("user", "gym_class", "gym_class__trainer")
    if date:
        qs = qs.filter(date=date)
    elif not request.GET.get("all"):
        qs = qs.filter(date__gte=today)
    if status:
        qs = qs.filter(status=status)
    if class_id.isdigit():
        qs = qs.filter(gym_class_id=int(class_id))
    qs = qs.order_by("date", "gym_class__start_time")
    return render(
        request,
        "dashboard/bookings.html",
        {
            "page_obj": _paginate(request, qs, 20),
            "date": date.isoformat() if date else "",
            "status": status,
            "class_id": class_id,
            "show_all": bool(request.GET.get("all")),
            "classes": GymClass.objects.all(),
            "status_choices": Booking.STATUS_CHOICES,
        },
    )


@staff_required
@require_POST
def booking_status(request, pk, status):
    booking = get_object_or_404(Booking, pk=pk)
    if status not in dict(Booking.STATUS_CHOICES):
        messages.error(request, "Invalid status.")
    else:
        booking.status = status
        booking.save(update_fields=["status"])
        messages.success(request, f"Booking marked as {booking.get_status_display().lower()}.")
    return redirect(request.POST.get("next") or reverse("dashboard:booking_list"))


# =====================================================================
# Attendance
# =====================================================================
@staff_required
def attendance_list(request):
    day = _get_date(request, "date", timezone.localdate())
    if request.method == "POST":
        form = CheckInForm(request.POST)
        if form.is_valid():
            record = form.save()
            if not Membership.current_for(record.user):
                messages.warning(request, f"Note: {record.user.username} has no active membership.")
            messages.success(request, f"{record.user.username} checked in.")
            return redirect(f"{reverse('dashboard:attendance_list')}?date={record.date.isoformat()}")
    else:
        form = CheckInForm()
    records = Attendance.objects.filter(date=day).select_related("user", "user__profile")
    return render(
        request,
        "dashboard/attendance.html",
        {
            "form": form,
            "records": records,
            "date": day.isoformat(),
            "in_gym": records.filter(check_out__isnull=True).count(),
        },
    )


@staff_required
@require_POST
def attendance_checkout(request, pk):
    record = get_object_or_404(Attendance, pk=pk)
    if not record.check_out:
        record.check_out = timezone.localtime().time().replace(microsecond=0)
        record.save(update_fields=["check_out"])
        messages.success(request, f"{record.user.username} checked out.")
    return redirect(f"{reverse('dashboard:attendance_list')}?date={record.date.isoformat()}")


class AttendanceUpdate(DashFormMixin, UpdateView):
    model = Attendance
    form_class = CheckInForm
    page_title = "Edit Attendance"
    list_url_name = "dashboard:attendance_list"
    success_message = "Attendance updated."


class AttendanceDelete(DashDeleteView):
    model = Attendance
    list_url_name = "dashboard:attendance_list"


# =====================================================================
# Contact messages
# =====================================================================
@staff_required
def message_list(request):
    show = request.GET.get("show", "")
    qs = ContactMessage.objects.all()
    if show == "unread":
        qs = qs.filter(is_read=False)
    return render(request, "dashboard/messages.html", {"page_obj": _paginate(request, qs), "show": show})


@staff_required
def message_detail(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    if not msg.is_read:
        msg.is_read = True
        msg.save(update_fields=["is_read"])
    return render(request, "dashboard/message_detail.html", {"msg": msg})


@staff_required
@require_POST
def message_toggle(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = not msg.is_read
    msg.save(update_fields=["is_read"])
    return redirect("dashboard:message_list")


class MessageDelete(DashDeleteView):
    model = ContactMessage
    list_url_name = "dashboard:message_list"


# =====================================================================
# Announcements
# =====================================================================
class AnnouncementList(StaffRequiredMixin, ListView):
    model = Announcement
    template_name = "dashboard/announcements.html"
    context_object_name = "announcements"


class AnnouncementCreate(DashFormMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    page_title = "New Announcement"
    list_url_name = "dashboard:announcement_list"
    success_message = 'Announcement "%(title)s" published.'


class AnnouncementUpdate(DashFormMixin, UpdateView):
    model = Announcement
    form_class = AnnouncementForm
    page_title = "Edit Announcement"
    list_url_name = "dashboard:announcement_list"
    success_message = 'Announcement "%(title)s" updated.'


class AnnouncementDelete(DashDeleteView):
    model = Announcement
    list_url_name = "dashboard:announcement_list"


# =====================================================================
# Reports
# =====================================================================
@staff_required
def reports(request):
    today = timezone.localdate()
    date_from = _get_date(request, "from", today.replace(day=1))
    date_to = _get_date(request, "to", today)

    paid = Payment.objects.filter(
        status="paid", paid_at__date__gte=date_from, paid_at__date__lte=date_to
    )
    method_map = dict(Payment.METHOD_CHOICES)
    by_method = [
        {"label": method_map.get(r["method"], r["method"]), "total": r["total"], "count": r["count"]}
        for r in paid.values("method").annotate(total=Sum("amount"), count=Count("id")).order_by("-total")
    ]
    by_plan = (
        paid.filter(membership__isnull=False)
        .values("membership__plan__name")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("-total")
    )
    status_map = dict(Membership.STATUS_CHOICES)
    membership_status = [
        {"label": status_map.get(r["status"], r["status"]), "count": r["c"]}
        for r in Membership.objects.values("status").annotate(c=Count("id")).order_by("status")
    ]
    top_classes = (
        Booking.objects.filter(date__gte=date_from, date__lte=date_to)
        .exclude(status="cancelled")
        .values("gym_class__name")
        .annotate(c=Count("id"))
        .order_by("-c")[:8]
    )
    context = {
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "revenue": paid.aggregate(s=Sum("amount"))["s"] or 0,
        "payments_count": paid.count(),
        "new_members": User.objects.filter(
            is_staff=False, date_joined__date__gte=date_from, date_joined__date__lte=date_to
        ).count(),
        "visits": Attendance.objects.filter(date__gte=date_from, date__lte=date_to).count(),
        "bookings": Booking.objects.filter(date__gte=date_from, date__lte=date_to)
        .exclude(status="cancelled")
        .count(),
        "by_method": by_method,
        "by_plan": by_plan,
        "membership_status": membership_status,
        "top_classes": top_classes,
    }
    return render(request, "dashboard/reports.html", context)

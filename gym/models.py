from datetime import datetime, timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

DAY_CHOICES = [
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
]


class MembershipPlan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    duration_days = models.PositiveIntegerField(help_text="Length of the plan in days (e.g. 30, 90, 365).")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.TextField(blank=True, help_text="One feature per line.")
    is_popular = models.BooleanField(default=False, help_text="Highlight this plan on the website.")
    is_active = models.BooleanField(default=True, help_text="Inactive plans are hidden from members.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} ({self.duration_days} days)"

    @property
    def feature_list(self):
        return [line.strip() for line in self.features.splitlines() if line.strip()]

    @property
    def duration_label(self):
        d = self.duration_days
        if d % 365 == 0:
            n = d // 365
            return f"{n} Year" + ("s" if n > 1 else "")
        if d % 30 == 0:
            n = d // 30
            return f"{n} Month" + ("s" if n > 1 else "")
        return f"{d} Days"


class Trainer(models.Model):
    GENDER_CHOICES = [("male", "Male"), ("female", "Female"), ("other", "Other")]

    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    specialization = models.CharField(max_length=150)
    experience_years = models.PositiveIntegerField(default=1)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="trainers/", blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    instagram = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class GymClass(models.Model):
    LEVEL_CHOICES = [
        ("all", "All Levels"),
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    trainer = models.ForeignKey(
        Trainer, on_delete=models.SET_NULL, null=True, blank=True, related_name="classes"
    )
    day_of_week = models.PositiveSmallIntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=20)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="all")
    location = models.CharField(max_length=100, default="Main Floor")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return f"{self.name} – {self.get_day_of_week_display()} {self.start_time:%I:%M %p}"

    def next_date(self):
        """Date of the next session of this weekly class (today if it hasn't started yet)."""
        now = timezone.localtime()
        today = now.date()
        days_ahead = (self.day_of_week - today.weekday()) % 7
        if days_ahead == 0 and now.time() >= self.start_time:
            days_ahead = 7
        return today + timedelta(days=days_ahead)

    def booked_count(self, date=None):
        date = date or self.next_date()
        return self.bookings.filter(date=date).exclude(status="cancelled").count()

    def seats_left(self, date=None):
        return max(0, self.capacity - self.booked_count(date))

    @property
    def duration_minutes(self):
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        return int((end - start).total_seconds() // 60)


class Membership(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Approval"),
        ("active", "Active"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name="memberships")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.get_username()} – {self.plan.name} ({self.get_status_display()})"

    @classmethod
    def expire_old(cls):
        """Mark memberships whose end date has passed as expired."""
        return cls.objects.filter(status="active", end_date__lt=timezone.localdate()).update(
            status="expired"
        )

    @classmethod
    def current_for(cls, user):
        """The user's currently running membership, if any."""
        today = timezone.localdate()
        return (
            cls.objects.filter(user=user, status="active", start_date__lte=today, end_date__gte=today)
            .select_related("plan")
            .order_by("-end_date")
            .first()
        )

    def activate(self, start=None):
        """Activate the membership. Renewals start the day after the current plan ends."""
        today = timezone.localdate()
        if start is None:
            latest = (
                Membership.objects.filter(user=self.user, status="active", end_date__gte=today)
                .exclude(pk=self.pk)
                .order_by("-end_date")
                .first()
            )
            start = latest.end_date + timedelta(days=1) if latest else today
        self.start_date = start
        self.end_date = start + timedelta(days=self.plan.duration_days - 1)
        self.status = "active"
        self.save()

    @property
    def is_current(self):
        today = timezone.localdate()
        return (
            self.status == "active"
            and self.start_date is not None
            and self.start_date <= today <= self.end_date
        )

    @property
    def days_left(self):
        if self.status != "active" or not self.end_date:
            return 0
        return max(0, (self.end_date - timezone.localdate()).days + 1)

    @property
    def progress_percent(self):
        if not (self.start_date and self.end_date) or self.status != "active":
            return 0
        total = (self.end_date - self.start_date).days + 1
        used = (timezone.localdate() - self.start_date).days + 1
        return max(0, min(100, round(used * 100 / total)))


class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Cash at Counter"),
        ("upi", "UPI"),
        ("card", "Debit / Credit Card"),
        ("bank", "Bank Transfer"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    membership = models.ForeignKey(
        Membership, on_delete=models.SET_NULL, null=True, blank=True, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default="cash")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    transaction_id = models.CharField("Transaction / Reference No.", max_length=100, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.invoice_no} – {self.user.get_username()} – {self.amount}"

    @property
    def invoice_no(self):
        return f"LI-INV-{self.pk:05d}" if self.pk else "LI-INV-NEW"

    def mark_paid(self):
        self.status = "paid"
        self.paid_at = timezone.now()
        self.save()
        if self.membership and self.membership.status == "pending":
            self.membership.activate()


class Booking(models.Model):
    STATUS_CHOICES = [
        ("booked", "Booked"),
        ("attended", "Attended"),
        ("cancelled", "Cancelled"),
        ("missed", "Missed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    gym_class = models.ForeignKey(GymClass, on_delete=models.CASCADE, related_name="bookings")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="booked")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "gym_class__start_time"]
        constraints = [
            models.UniqueConstraint(fields=["user", "gym_class", "date"], name="unique_booking_per_day")
        ]

    def __str__(self):
        return f"{self.user.get_username()} – {self.gym_class.name} on {self.date}"

    @property
    def can_cancel(self):
        return self.status == "booked" and self.date >= timezone.localdate()


class Attendance(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendances"
    )
    date = models.DateField(default=timezone.localdate)
    check_in = models.TimeField()
    check_out = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ["-date", "-check_in"]
        verbose_name_plural = "Attendance"

    def __str__(self):
        return f"{self.user.get_username()} – {self.date}"

    @property
    def duration_minutes(self):
        if not self.check_out:
            return None
        start = datetime.combine(self.date, self.check_in)
        end = datetime.combine(self.date, self.check_out)
        return max(0, int((end - start).total_seconds() // 60))


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    subject = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} – {self.name}"


class Announcement(models.Model):
    title = models.CharField(max_length=150)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

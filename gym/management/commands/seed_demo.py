from datetime import time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Profile
from gym.models import (
    Announcement,
    Attendance,
    GymClass,
    Membership,
    MembershipPlan,
    Payment,
    Trainer,
)

User = get_user_model()


class Command(BaseCommand):
    help = "Load demo data: plans, trainers, weekly classes, announcements, an admin and a demo member."

    def add_arguments(self, parser):
        parser.add_argument("--admin-password", default="Admin@123", help="Password for the 'admin' user.")
        parser.add_argument("--member-password", default="Member@123", help="Password for the 'member' user.")

    def handle(self, *args, **opts):
        from django.core.management.base import CommandError
        from django.db import connection

        missing = {"appearance_sitesettings", "gym_membershipplan"} - set(connection.introspection.table_names())
        if missing:
            raise CommandError(
                "Database tables are missing. Run these first:\n"
                "  python manage.py makemigrations accounts gym appearance\n"
                "  python manage.py migrate"
            )
        self._plans()
        trainers = self._trainers()
        self._classes(trainers)
        self._announcements()
        self._users(opts["admin_password"], opts["member_password"])
        from appearance.utils import ensure_defaults
        ensure_defaults(force=True)
        self.stdout.write("  • website appearance (editable sections, menus, colours)")
        self.stdout.write(self.style.SUCCESS("Demo data ready."))

    def _plans(self):
        plans = [
            ("Monthly", 30, 1500, False, "Perfect to get started.",
             "Full gym floor access\nCardio & strength zones\nLocker access\n1 body assessment"),
            ("Quarterly", 90, 4000, True, "Our most popular plan – save more.",
             "Everything in Monthly\nUnlimited group classes\nDiet consultation\n2 body assessments"),
            ("Half-Yearly", 180, 7500, False, "Commit to real change.",
             "Everything in Quarterly\n2 personal training sessions\nFree LoadImpact T-shirt"),
            ("Annual", 365, 13000, False, "Best value for the dedicated.",
             "Everything in Half-Yearly\n6 personal training sessions\nFreeze up to 30 days\nGuest pass x 4"),
        ]
        for name, days, price, popular, desc, features in plans:
            MembershipPlan.objects.get_or_create(
                name=name,
                defaults=dict(duration_days=days, price=price, is_popular=popular,
                              description=desc, features=features),
            )
        self.stdout.write("  • membership plans")

    def _trainers(self):
        data = [
            ("Arjun Menon", "male", "Strength & Powerlifting", 8,
             "National-level powerlifter helping members build real strength safely."),
            ("Priya Nair", "female", "Yoga & Mobility", 6,
             "Certified yoga instructor focused on flexibility, posture and breathwork."),
            ("Rahul Das", "male", "CrossFit & HIIT", 5,
             "High-energy coach for conditioning, fat loss and athletic performance."),
            ("Sneha Thomas", "female", "Zumba & Weight Loss", 4,
             "Dance-fitness expert who makes cardio the best part of your day."),
        ]
        trainers = {}
        for name, gender, spec, exp, bio in data:
            t, _ = Trainer.objects.get_or_create(
                name=name, defaults=dict(gender=gender, specialization=spec, experience_years=exp, bio=bio)
            )
            trainers[name] = t
        self.stdout.write("  • trainers")
        return trainers

    def _classes(self, t):
        schedule = [
            ("Morning Yoga", "Priya Nair", [0, 2, 4], time(6, 30), time(7, 30), "all", "Studio A"),
            ("Power Lifting Basics", "Arjun Menon", [0, 3], time(18, 0), time(19, 0), "beginner", "Strength Zone"),
            ("HIIT Blast", "Rahul Das", [1, 3, 5], time(7, 0), time(7, 45), "intermediate", "Functional Area"),
            ("Zumba Party", "Sneha Thomas", [1, 4], time(18, 30), time(19, 30), "all", "Studio A"),
            ("CrossFit WOD", "Rahul Das", [2, 5], time(19, 0), time(20, 0), "advanced", "Functional Area"),
            ("Mobility & Stretch", "Priya Nair", [6], time(8, 0), time(9, 0), "all", "Studio A"),
        ]
        for name, trainer, days, start, end, level, loc in schedule:
            for d in days:
                GymClass.objects.get_or_create(
                    name=name, day_of_week=d, start_time=start,
                    defaults=dict(trainer=t[trainer], end_time=end, level=level, location=loc, capacity=20),
                )
        self.stdout.write("  • weekly class schedule")

    def _announcements(self):
        Announcement.objects.get_or_create(
            title="Welcome to LoadImpact!",
            defaults={"content": "Our unisex gym is now open 7 days a week. Book your first class online from your dashboard."},
        )
        Announcement.objects.get_or_create(
            title="New Zumba batch",
            defaults={"content": "A new evening Zumba batch starts every Tuesday and Friday at 6:30 PM with coach Sneha."},
        )
        self.stdout.write("  • announcements")

    def _users(self, admin_pw, member_pw):
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser(
                "admin", "admin@loadimpact.in", admin_pw, first_name="Gym", last_name="Admin"
            )
            Profile.objects.get_or_create(user=admin)
            self.stdout.write(f"  • superuser  admin / {admin_pw}")

        if not User.objects.filter(username="member").exists():
            member = User.objects.create_user(
                "member", "member@example.com", member_pw, first_name="Anu", last_name="Joseph"
            )
            profile, _ = Profile.objects.get_or_create(user=member)
            profile.phone = "9876500000"
            profile.gender = "female"
            profile.height_cm = 162
            profile.weight_kg = 58
            profile.fitness_goal = "weight_loss"
            profile.save()

            plan = MembershipPlan.objects.get(name="Quarterly")
            ms = Membership.objects.create(user=member, plan=plan, status="pending")
            ms.activate(start=timezone.localdate() - timedelta(days=20))
            Payment.objects.create(
                user=member, membership=ms, amount=plan.price, method="upi", status="paid",
                transaction_id="UPI123456789", paid_at=timezone.now() - timedelta(days=20),
            )
            for i in range(1, 6):
                Attendance.objects.create(
                    user=member, date=timezone.localdate() - timedelta(days=i * 2),
                    check_in=time(7, 0), check_out=time(8, 15),
                )
            self.stdout.write(f"  • demo member  member / {member_pw}")

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render

from appearance.utils import page_context

from .forms import ContactForm
from .models import DAY_CHOICES, Announcement, GymClass, MembershipPlan, Trainer

User = get_user_model()


def _tokens():
    """Live numbers that can be used in editable text as {members}, {trainers}, {classes}."""
    return {
        "members": User.objects.filter(is_staff=False).count(),
        "trainers": Trainer.objects.filter(is_active=True).count(),
        "classes": GymClass.objects.filter(is_active=True).count(),
    }


def _render_page(request, page, template, extra=None):
    context = {"page_key": page}
    context.update(page_context(page, _tokens()))
    context.update(extra or {})
    return render(request, template, context)


def home(request):
    return _render_page(request, "home", "gym/home.html", {
        "plans": MembershipPlan.objects.filter(is_active=True)[:3],
        "trainers": Trainer.objects.filter(is_active=True)[:4],
        "announcements": Announcement.objects.filter(is_active=True)[:3],
    })


def about(request):
    return _render_page(request, "about", "gym/about.html")


def plans(request):
    return _render_page(request, "plans", "gym/plans.html", {
        "plans": MembershipPlan.objects.filter(is_active=True),
    })


def trainers(request):
    return _render_page(request, "trainers", "gym/trainers.html", {
        "trainers": Trainer.objects.filter(is_active=True),
    })


def schedule(request):
    classes = GymClass.objects.filter(is_active=True).select_related("trainer")
    week = [
        {"day": day_name, "classes": [c for c in classes if c.day_of_week == day_num]}
        for day_num, day_name in DAY_CHOICES
    ]
    return _render_page(request, "schedule", "gym/schedule.html", {"week": week})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you! Your message has been sent. We'll get back to you soon.")
            return redirect("gym:contact")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {"name": request.user.get_full_name(), "email": request.user.email}
        form = ContactForm(initial=initial)
    return _render_page(request, "contact", "gym/contact.html", {"form": form})

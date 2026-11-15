from django.urls import path

from . import views

app_name = "gym"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("plans/", views.plans, name="plans"),
    path("trainers/", views.trainers, name="trainers"),
    path("schedule/", views.schedule, name="schedule"),
    path("contact/", views.contact, name="contact"),
]

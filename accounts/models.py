from datetime import date

from django.conf import settings
from django.db import models


class Profile(models.Model):
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]
    GOAL_CHOICES = [
        ("general", "General Fitness"),
        ("weight_loss", "Weight Loss"),
        ("muscle_gain", "Muscle Gain"),
        ("strength", "Strength"),
        ("endurance", "Endurance"),
        ("flexibility", "Flexibility"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField(max_length=15, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    height_cm = models.DecimalField(
        "Height (cm)", max_digits=5, decimal_places=1, null=True, blank=True
    )
    weight_kg = models.DecimalField(
        "Weight (kg)", max_digits=5, decimal_places=1, null=True, blank=True
    )
    fitness_goal = models.CharField(max_length=20, choices=GOAL_CHOICES, default="general")
    emergency_contact = models.CharField(max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.get_username()}"

    @property
    def member_id(self):
        return f"LI{self.user_id:05d}"

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @property
    def bmi(self):
        if self.height_cm and self.weight_kg and self.height_cm > 0:
            height_m = float(self.height_cm) / 100
            return round(float(self.weight_kg) / (height_m * height_m), 1)
        return None

    @property
    def bmi_category(self):
        bmi = self.bmi
        if bmi is None:
            return ""
        if bmi < 18.5:
            return "Underweight"
        if bmi < 25:
            return "Normal"
        if bmi < 30:
            return "Overweight"
        return "Obese"

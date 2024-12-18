from django.contrib.auth.models import User
from django.db import models


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    medical_conditions = models.JSONField(default=list, blank=True)
    medications = models.JSONField(default=list, blank=True)
    allergies = models.JSONField(default=list, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    relationship_to_patient = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(default='profile_images/default.png', upload_to='profile_images')
    bio = models.TextField(blank=True)
    is_profile_complete = models.BooleanField(default=False)
    last_visit_date = models.DateField(null=True, blank=True)
    preferred_hospital = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Patient Profile: {self.user.username}"


class PatientHealthInfo(models.Model):
    patient = models.OneToOneField(PatientProfile, on_delete=models.CASCADE, related_name="health_info")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Height in cm
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Weight in kg
    bmi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)  # BMI (calculated or manual)
    blood_pressure = models.CharField(max_length=15, blank=True)  # e.g., 120/80
    heart_rate = models.PositiveIntegerField(null=True, blank=True)  # Beats per minute
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)  # Body temperature in °C
    oxygen_saturation = models.PositiveIntegerField(null=True, blank=True)  # SpO2 percentage
    glucose_level = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Blood glucose level

    def calculate_bmi(self):
        """Optional utility method to calculate BMI."""
        if self.height and self.weight:
            height_in_meters = self.height / 100  # Convert height from cm to meters
            return round(self.weight / (height_in_meters ** 2), 2)
        return None

    def save(self, *args, **kwargs):
        # Auto-calculate BMI if height and weight are provided
        if self.height and self.weight:
            self.bmi = self.calculate_bmi()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Health Info for {self.patient.user.username}"

from django.db import models


class Lesion(models.Model):
    lesion_id = models.CharField(max_length=100)
    image_id = models.CharField(max_length=100)
    dx = models.CharField(max_length=50)  # Diagnosis
    dx_type = models.CharField(max_length=50)  # Diagnosis Type
    age = models.IntegerField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], null=True, blank=True)
    localization = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.lesion_id} - {self.dx}"


class UploadedImage(models.Model):
    image = models.ImageField(upload_to='images/')  # Store images in the "images/" folder

    def __str__(self):
        return f"Image {self.id}"

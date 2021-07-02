# from typing_extensions import Required
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Benificial(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_number = models.IntegerField(default=0)
    registration_timing=models.DateTimeField(null=True)
    contact_1=models.IntegerField(default=0)
    contact_2=models.IntegerField(default=0)
    is_registered=models.BooleanField(default=False)
    is_delivered=models.BooleanField(default=False)
    slot_timing = models.DateTimeField(null=True)

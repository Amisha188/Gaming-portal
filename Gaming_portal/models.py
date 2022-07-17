from django.db import models
from statistics import mode
from django.forms import ModelForm

# Create your models here.
class Gamers_list(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=200)
    email = models.CharField(max_length=100)
    tetrisMaxScore = models.BigIntegerField(default=0)



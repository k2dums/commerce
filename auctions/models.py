from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    pass

class Listing(models.Model):
    name=models.CharField(max_length=64)
    price=models.IntegerField()
    description=models.CharField(max_length=64)
    time=models.CharField(max_length=64)
    
# class Bids(models.Model):
#    pass
# class Comment(models.Model):
#     pass

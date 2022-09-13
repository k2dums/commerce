from tokenize import blank_re
from unicodedata import category
from django.contrib.auth.models import AbstractUser
from django.db import models


def get_sentinel_category():
    return Category.objects.get_or_create(name="None")[0]
def get_sentinel_category_id():
    return get_sentinel_category().id
class User(AbstractUser):
    pass

class Category(models.Model):
    name=models.CharField(max_length=64)
    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    name=models.CharField(max_length=64)
    price=models.IntegerField()
    description=models.CharField(max_length=64)
    time=models.CharField(max_length=64)
    bid_start=models.IntegerField()
    category=models.ForeignKey(Category,on_delete=models.SET(get_sentinel_category),default=get_sentinel_category_id,related_name="listing_category")
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    users_watchlisting=models.ManyToManyField(User,blank=True,related_name="watchlist")
    img_url=models.CharField(max_length=200,null=True)
    category=models.ForeignKey(Category,on_delete=get_sentinel_category,default=get_sentinel_category_id,related_name="items")
    def __str__(self):
        return f"Item-id({self.id}):Name({self.name}):Price({self.price})"

class Bids(models.Model):
    name=models.ForeignKey(Listing,on_delete=models.CASCADE,related_name='bids')
    price=models.IntegerField()
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        return f"{self.name} BidPrice({self.price}) by {self.user}"

class Comment(models.Model):
    name=models.ForeignKey(Listing,on_delete=models.CASCADE,related_name='comments')
    comment=models.TextField(max_length=1000)
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    
    def __str__(self):
        return f"Comment-id:{self.id} by {self.user}"



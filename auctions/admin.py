from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Listing

class ListingAdmin(admin.ModelAdmin):
    list_display=("name","price","time")

# Register your models here.
admin.site.register(User,UserAdmin)
admin.site.register(Listing,ListingAdmin)
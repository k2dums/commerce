from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category, User,Listing,Bids,Comment

class ListingAdmin(admin.ModelAdmin):
    list_display=("name","price","time","user")
    filter_horizontal=("users_watchlisting",)
class BidsAdmin(admin.ModelAdmin):
    list_display=("name","price","user")
class CommentAdmin(admin.ModelAdmin):
    list_display=("name","comment","user")
class CategoryAdmin(admin.ModelAdmin):
    list_display=("name")
    
# Register your models here.
admin.site.register(User,UserAdmin)
admin.site.register(Listing,ListingAdmin)
admin.site.register(Bids,BidsAdmin)
admin.site.register(Comment,CommentAdmin)
admin.site.register(Category)
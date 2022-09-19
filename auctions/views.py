
from urllib import request
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Category, User,Listing,Bids,Comment
import datetime


def index(request):
    return render(request, "auctions/index.html",{"listings":Listing.objects.all(),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create_listing(request):
    if not(request.user.is_authenticated):
        return render(request,"auctions/login.html",{ 
            "message":"Need to be logged in to create Listing"
        })
    if request.method=="POST":
        name=request.POST.get("name")
        price=request.POST.get("price")
        description=request.POST.get("description")
        user=request.POST.get("user")
        img_url=request.POST.get("img_url")
        category=Category.objects.get(pk=request.POST.get("category"))
        #Provided the username is unique
        user=User.objects.get(username=user)
        listing=Listing()
        listing.name=name
        listing.price=price
        listing.bid_start=price
        listing.description=description
        listing.time=datetime.datetime.now()
        listing.user=user
        listing.img_url=img_url
        listing.category=category
        listing.save()
        return render(request,"auctions/index.html",{
            "message":f"{name} has been listed",
            "listings":Listing.objects.all(),
            
        })
    return render(request,"auctions/create_listing.html",{
        "categories":Category.objects.all(),
    })

def listing(request,listing_id):
    if not(request.user.is_authenticated):
        return render(request,"auctions/login.html",{ 
            "message":"Need to be logged in to see Listing"
        })
    listing=Listing.objects.get(pk=listing_id)
    user=User.objects.get(pk=request.user.id)
    if request.method=="POST":
        if "watchlist" in request.POST:
            print(f'[ADDED]{listing.name} will be added {request.user} watchlist')
            listing.users_watchlisting.add(user)
        elif "bid" in request.POST:
            bid_price=request.POST.get('bid_price')
            if bid_price:
                print(f"[SAVING]Placing Bid {bid_price} by {request.user}")
            else:
                print("No bids placed")
        elif "comment_user" in request.POST:
            comment=request.POST.get("comment")
            comment_obj=Comment()
            comment_obj.name=listing
            comment_obj.comment=comment
            comment_obj.user=user
            comment_obj.save()
            if comment:
                print(f"{comment}~{request.user}")
            else:
                print("No comments by user")
        
        elif "remove_watchlist" in request.POST:
            print(f'[REMOVED]{listing.name} will be removed {request.user} watchlist')
            listing.users_watchlisting.remove(user)
    return render(request,"auctions/listing.html",{
        "listing":listing,
        "bid_current_name":"Dummy Text",
        "no_bids":len(listing.bids.all()),
        "bids":listing.bids.all(),
        "comments":listing.comments.all(),
        "time":listing.time[11:16],
         "date":listing.time[0:10],
         "in_watchlist":False,
    })

@login_required
def watchlist(request):
    user=User.objects.get(pk=request.user.id)
    print(user.watchlist.all())
    print(type(user))
    return render(request,"auctions/watchlist.html",{"watchlists":user.watchlist.all()})

def category(request):
    category=''
    if request.method=='POST':
        category=Category.objects.get(pk=request.POST.get("category"))
        category=category.items.all()
    return render(request,"auctions/category.html",{
        "categories":Category.objects.all(),
        "items":category,
    })
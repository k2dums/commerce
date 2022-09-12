from cgi import print_exception
from unicodedata import name
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User,Listing,Bids
import datetime


def index(request):
    return render(request, "auctions/index.html",{"listings":Listing.objects.all()})


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

def create_listing(request):
    if not(request.user.is_authenticated):
        return render(request,"auctions/login.html",{ 
            "message":"Need to be logged in to create Listing"
        })
    if request.method=="POST":
        name=request.POST["name"]
        price=request.POST["price"]
        description=request.POST["description"]
        user=request.POST["user"]
        #Provided the username is unique
        user=User.objects.get(username=user)
        listing=Listing()
        listing.name=name
        listing.price=price
        listing.bid_start=price
        listing.description=description
        listing.time=datetime.datetime.now()
        listing.user=user
        listing.save()
        return render(request,"auctions/index.html",{
            "message":f"{name} has been listed",
            "listings":Listing.objects.all()
        })
    return render(request,"auctions/create_listing.html")

def listing(request,listing_id):
    listing=Listing.objects.get(pk=listing_id)
    if request.method=="POST":
        if "watchlist" in request.POST:
            print(f'{listing.name} will be added {request.user} watchlist')
        elif "bid" in request.POST:
            bid_price=request.POST.get('bid_price')
            if bid_price:
                print(f"Placing Bid {bid_price} by {request.user}")
            else:
                print("No bids placed")
        elif "comment_user" in request.POST:
            comment=request.POST.get("comment")
            if comment:
                print(f"{comment}~{request.user}")
            else:
                print("No comments by user")
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

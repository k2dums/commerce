from cgi import print_exception
from unicodedata import name
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User,Listing
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

def listing(request):
    if not(request.user.is_authenticated):
        return render(request,"auctions/login.html",{ 
            "message":"Need to be logged in to create Listing"
        })
    if request.method=="POST":
        name=request.POST["name"]
        price=request.POST["price"]
        description=request.POST["description"]
        listing=Listing()
        listing.name=name
        listing.price=price
        listing.description=description
        listing.time=datetime.datetime.now()
        listing.save()
        return render(request,"auctions/index.html",{
            "message":f"{name} has been listed",
            "listings":Listing.objects.all()
        })
    return render(request,"auctions/listing.html")

    
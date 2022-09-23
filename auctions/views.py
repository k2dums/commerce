

from urllib import request
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Min, Sum
from .models import Category, User,Listing,Bids,Comment
import datetime

from auctions import models

def findbidder(listing):
    allbids=listing.bids.all()
    if allbids:
        return allbids.filter(price=listing.price)
    else:
        return None
   
def findwinner(listing):
    return listing.bids.filter(price=listing.bids.all().aggregate(Max('price')).get("price__max"))
def index(request):
    return render(request, "auctions/index.html",{"listings":Listing.objects.filter(status="Active"),
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
        "categories":Category.objects.exclude(name="None"),
    })

def listing(request,listing_id):
    if not(request.user.is_authenticated):
        return render(request,"auctions/login.html",{ 
            "message":"Need to be logged in to see Listing"
        })
    winning_message=message=""
    listing=Listing.objects.get(pk=listing_id)
    user=User.objects.get(pk=request.user.id)
    you_won=False
    close_listing = True if (listing in user.listing.all() and listing.status == "Active") else False
    if listing.status==models.set_Listing_inactive():
        winner=findwinner(listing)
        if len(winner)>0:
            winner=winner[0].user
        else:
            winner=None
        if winner==user:
            winning_message=f"You won the bid"
            you_won=True
        elif winner==None:
            winning_message="Closed before any bids"
        else:
            winning_message=f"{winner} won the bid" 

    if request.method=="POST":
        if "watchlist" in request.POST:
            print(f'[ADDED]{listing.name} will be added {request.user} watchlist')
            listing.users_watchlisting.add(user)
        elif "bid" in request.POST:
            bid_price=int(request.POST.get('bid_price'))
            if bid_price>listing.bid_start and bid_price>listing.price and listing.user is not user:
                    print(f"[SAVING]Placing Bid {bid_price} by {request.user}")
                    bid=Bids()
                    bid.name=listing
                    bid.user=user
                    bid.price=bid_price
                    bid.save()
                    listing.price=bid_price
                    listing.save()
            else:
                message="Invalid Bid amount, must be greater than the last bid  and starting bid"
        elif "comment_user" in request.POST:
            comment=request.POST.get("comment")
            comment_obj=Comment()
            comment_obj.name=listing
            comment_obj.comment=comment
            comment_obj.user=user
            if comment:
                comment_obj.save()
                print(f"{comment}~{request.user}")
            else:
                print("No comments by user")
        
        elif "remove_watchlist" in request.POST:
            print(f'[REMOVED]{listing.name} will be removed {request.user} watchlist')
            listing.users_watchlisting.remove(user)
        elif "close_listing" in request.POST:
            listing.status=models.set_Listing_inactive()
            listing.save()

        return HttpResponseRedirect(reverse("listing",kwargs={"listing_id":listing_id}))

    bidder=findbidder(listing)
    if bidder:
        bidder=findbidder(listing)[0].user
    else :
        bidder=None
    user_listing= True if listing in user.listing.all() else False
    return render(request,"auctions/listing.html",{
        "listing":listing,
        "bidder":bidder,
        "no_bids":len(listing.bids.all()),
        "bids":listing.bids.all(),
        "comments":listing.comments.all(),
        "time":listing.time[11:16],
         "date":listing.time[0:10],
         "in_watchlist":listing in user.watchlist.all(),
         "message":message,
         "close_listing":close_listing,
         "user_listing":user_listing,
         "active":True if listing.status=="Active" else False,
         "winning_message":winning_message,
         "you_won":you_won,
    })

@login_required
def watchlist(request):
    user=User.objects.get(pk=request.user.id)
    return render(request,"auctions/watchlist.html",{"watchlists":user.watchlist.all()})

def category(request):
    category=None
    listings=None
    if request.method=='POST':
        category=Category.objects.get(pk=request.POST.get("category"))
        listings=category.items.all()
    if category is None:
        listings=Listing.objects.all()
    return render(request,"auctions/category.html",{
        "categories":Category.objects.exclude(name="None"),
        "listings":listings,
    })

@login_required
def your_listing(request):
    user=User.objects.get(pk=request.user.id)
    return render(request,"auctions/your_listing.html",{
        "listings":user.listing.all(),
        })
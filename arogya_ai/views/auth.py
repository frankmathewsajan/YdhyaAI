from django.contrib.auth import authenticate, login as user_login, logout as user_logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from arogya_ai.models import PatientProfile


def login(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            user_login(request, user)
            print(user)
            return redirect('index')
        else:
            return render(request, "auth/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auth/login.html") if request.user.is_anonymous else redirect('index')


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        first_name = request.POST['user_name']

        if password != confirmation:
            return render(request, "auth/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username, password=password)
            profile = PatientProfile(user=user, first_name=first_name)
            user.save()
            profile.save()
        except IntegrityError as e:
            print(e)
            return render(request, "auth/register.html", {
                "message": "Username already taken."
            })
        user_login(request, user)
        return HttpResponseRedirect(reverse("setup"))
    else:
        return render(request, "auth/register.html") if request.user.is_anonymous else redirect('index')


def logout(request):
    user_logout(request)
    return redirect('index')

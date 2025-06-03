from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse

from .models import Group, Message


@login_required
def chat_room(request, room_name):
    """
    Renders the chat room page
    """

    # TODO: have a list of available rooms or allow users to create them.
    group, created = Group.objects.get_or_create(name=room_name)

    messages = Message.objects.filter(group=group).order_by("timestamp")[:50]

    return render(
        request,
        "chat/room.html",
        {
            "room_name": room_name,
            "username": request.user.username,
            "messages": messages,
        },
    )


@login_required
def index(request):
    """
    A simple index page to list available rooms or allow creating new ones.
    For now, it just shows a few example rooms and a way to enter a custom one.
    """
    # Example groups, you can fetch these from the Group model
    # groups = Group.objects.all()
    example_groups = [
        {"name": "general"},
        {"name": "random"},
        {"name": "project-alpha"},
    ]

    return render(
        request,
        "chat/index.html",
        {
            "example_groups": example_groups,
        },
    )


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect(reverse("chat:index"))

    else:
        form = UserCreationForm()

    return render(request, "chat/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect(request.GET.get("next", reverse("chat:index")))
    else:
        form = AuthenticationForm()
    return render(request, "chat/login.html", {"form": form})


@login_required
def logout_view(request):
    auth_logout(request)
    return redirect(reverse("chat:login"))

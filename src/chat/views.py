import logging
import time

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .models import Group, Message

logger_views = logging.getLogger(f"{__name__}.views")


def get_redis_client_sync_from_settings():
    redis_client = getattr(settings, "REDIS_CLIENT", None)
    if redis_client is None:
        logger_views.error("REDIS_CLIENT (sync) not configured/connected.")
    return redis_client


@login_required
@cache_page(60 * 1)
def index(request):
    all_groups_cached = cache.get("all_chat_groups")
    if not all_groups_cached:
        all_groups_list = list(Group.objects.all().values("name", "id"))
        cache.set("all_chat_groups", all_groups_list, timeout=60 * 5)
        logger_views.info("Fetched groups from DB for index and cached.")
        all_groups_cached = all_groups_list
    else:
        logger_views.info("Fetched groups from CACHE for index.")
    example_groups = [{"name": g["name"]} for g in all_groups_cached[:5]]
    current_time_for_fragment_cache = time.time()
    return render(
        request,
        "chat/index.html",
        {
            "example_groups": example_groups,
            "all_groups": all_groups_cached,
            "current_time_for_fragment_cache": current_time_for_fragment_cache,
        },
    )


@login_required
def chat_room(request, room_name):
    group, created = Group.objects.get_or_create(name=room_name)
    # messages = list(reversed(Message.objects.filter(group=group).order_by('timestamp').select_related('author')[:50]))
    messages = list(
        Message.objects.filter(group=group)
        .order_by("timestamp")
        .select_related("author")[:50]
    )
    online_users_list = []
    if redis_client := get_redis_client_sync_from_settings():
        try:
            redis_key = f"presence:chat:{room_name}"
            online_usernames_set = sync_to_async(redis_client.smembers)(redis_key)
            online_users_list = sorted(list(online_usernames_set))
            logger_views.debug(
                f"Fetched online users for {room_name} (view): {online_users_list}"
            )
        except Exception as e:
            logger_views.error(
                f"Redis error fetching presence for {room_name} (view): {e}"
            )
    else:
        logger_views.warning(
            f"Redis client not available for fetching presence in {room_name} (view)."
        )
    return render(
        request,
        "chat/room.html",
        {
            "room_name": room_name,
            "username": request.user.username,
            "messages": messages,
            "online_users_list": online_users_list,
        },
    )


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            logger_views.info(f"New user registered: {user.username}")
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
            logger_views.info(f"User logged in: {user.username}")
            return redirect(request.GET.get("next", reverse("chat:index")))
    else:
        form = AuthenticationForm()
    return render(request, "chat/login.html", {"form": form})


@login_required
def logout_view(request):
    logout_target_name = "chat:login"
    logger_views.info(f"User logged out: {request.user.username}")
    auth_logout(request)
    return redirect(logout_target_name)

from allauth.account.utils import send_email_confirmation
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import EmailForm, ProfileForm, UsernameForm


def profile_view(request, username=None):

    if username:
        profile = get_object_or_404(User, username=username).profile

    else:
        try:
            profile = request.user.profile
        except Exception:
            return redirect_to_login(request.get_full_path())

    return render(request, "users/profile.html", {"profile": profile})


@login_required
def profile_edit_view(request):

    form = ProfileForm(instance=request.user.profile)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect("users:profile")

    onboarding = request.path == reverse("users:profile-onboarding")
    return render(
        request, "users/profile_edit.html", {"form": form, "onboarding": onboarding}
    )


@login_required
def profile_settings_view(request):
    return render(request, "users/profile_settings.html")


@login_required
def profile_emailchange(request):

    if request.htmx:
        form = EmailForm(instance=request.user)
        return render(request, "partials/email_form.html", {"form": form})

    if request.method == "POST":
        form = EmailForm(request.POST, instance=request.user)

        if form.is_valid():

            # Check if the email already exists
            email = form.cleaned_data["email"]
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.warning(request, f"{email} is already in use.")
                return redirect("users:profile-settings")

            form.save()

            # Then Signal updates emailaddress and set verified to False

            # Then send confirmation email
            send_email_confirmation(request, request.user)

        else:
            messages.warning(request, "Email not valid or already in use")
        return redirect("users:profile-settings")

    return redirect("users:profile-settings")


@login_required
def profile_usernamechange(request):
    if request.htmx:
        form = UsernameForm(instance=request.user)
        return render(request, "partials/username_form.html", {"form": form})

    if request.method == "POST":
        form = UsernameForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Username updated successfully.")
        else:
            messages.warning(request, "Username not valid or already in use")
        return redirect("users:profile-settings")
    return redirect("users:profile-settings")


@login_required
def profile_emailverify(request):
    send_email_confirmation(request, request.user)
    return redirect("users:profile-settings")


@login_required
def profile_delete_view(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        logout(request)
        messages.success(request, "Account deleted, what a pity")
        return redirect("home")

    return render(request, "users/profile_delete.html")

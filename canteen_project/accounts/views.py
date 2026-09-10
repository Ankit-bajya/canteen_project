# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        room_or_class = request.POST.get('room_or_class')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Ye Username pehle se Liya hua hai.")
            return redirect('register')

        if CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Ye Phone Number pehle se registered hai.")
            return redirect('register')

        # Naya User Create Karo
        user = CustomUser.objects.create_user(
            username=username,
            phone_number=phone_number,
            password=password,
            room_or_class=room_or_class
        )
        login(request, user) # Direct Login Registration ke baad
        messages.success(request, f"Welcome {user.username}! Account ban gaya hai.")
        return redirect('dashboard_home')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username') # Mobile or Username
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard_home')
        else:
            messages.error(request, "Galat Username/Phone ya Password!")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "Aap logout ho chuke hain.")
    return redirect('login')

@login_required(login_url='login')
def profile_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        room_or_class = request.POST.get('room_or_class')

        user = request.user
        user.phone_number = phone_number
        user.room_or_class = room_or_class
        user.save()

        messages.success(request, "Profile successfully update ho gayi!")
        return redirect('profile')

    return render(request, 'accounts/profile.html')
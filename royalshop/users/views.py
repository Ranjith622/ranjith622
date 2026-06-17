"""
Users App - Views
==================
Customer registration, login, logout, and profile.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def user_register(request):
    """Customer registration"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        password1  = request.POST.get('password1')
        password2  = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(
                username=username, email=email,
                password=password1,
                first_name=first_name, last_name=last_name,
            )
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name or user.username}! Account created.')
            return redirect('home')

    return render(request, 'users/register.html')


def user_login(request):
    """Customer login"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html')


def user_logout(request):
    """Customer logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


def user_profile(request):
    """Customer profile page"""
    if not request.user.is_authenticated:
        return redirect('user_login')
    from orders.models import Order
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    return render(request, 'users/profile.html', {'orders': orders})

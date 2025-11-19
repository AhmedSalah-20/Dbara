# accounts/views.py ← REPLACE EVERYTHING WITH THIS

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db import transaction
from .models import UserProfile, Recipe, RecipeImage


def home(request):
    if request.user.is_authenticated:
        # Admin → admin panel
        if request.user.is_staff:
            return redirect('/admin/')
        # Chef → dashboard
        try:
            if request.user.userprofile.role == 'chef':
                return redirect('accounts:chef_dashboard')
        except UserProfile.DoesNotExist:
            pass
    return render(request, 'base/home.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role = request.POST.get('role', 'visitor')  # visitor / chef / nutritionist

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'accounts/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, 'accounts/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already used")
            return render(request, 'accounts/signup.html')

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password1)
            UserProfile.objects.create(user=user, role=role)

            # If someone registers as nutritionist → just welcome
            login(request, user)
            messages.success(request, f"Welcome {username}!")

            if role == 'chef':
                return redirect('accounts:chef_dashboard')
            return redirect('accounts:home')

    return render(request, 'accounts/signup.html')


def login_view(request):
    if request.method == 'POST':
        identifier = request.POST['username'].strip()
        password = request.POST['password']

        user = authenticate(request, username=identifier, password=password)
        if not user:
            try:
                user = User.objects.get(email=identifier)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'visitor'})

            # ADMIN → go to Django admin
            if user.is_staff:
                return redirect('/admin/')

            # CHEF → dashboard
            try:
                if user.userprofile.role == 'chef':
                    return redirect('accounts:chef_dashboard')
            except UserProfile.DoesNotExist:
                pass

            return redirect('accounts:home')
        else:
            messages.error(request, "Wrong credentials")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('accounts:home')


# ====================== CHEF DASHBOARD ======================
@login_required
def chef_dashboard(request):
    if request.user.is_staff:
        return redirect('/admin/')

    try:
        if request.user.userprofile.role != 'chef':
            messages.error(request, "Only chefs can access this page")
            return redirect('accounts:home')
    except UserProfile.DoesNotExist:
        return redirect('accounts:home')

    recipes = Recipe.objects.filter(author=request.user).order_by('-created_at')
    total_views = recipes.aggregate(total=Sum('views'))['total'] or 0

    context = {
        'recipes': recipes,
        'total_recipes': recipes.count(),
        'total_views': total_views,
    }
    return render(request, 'chef/dashboard.html', context)


@login_required
def create_recipe(request):
    if request.user.is_staff or (hasattr(request.user, 'userprofile') and request.user.userprofile.role != 'chef'):
        return redirect('accounts:home')

    if request.method == 'POST':
        recipe = Recipe.objects.create(
            author=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            prep_time=request.POST['prep_time'],
            cook_time=request.POST['cook_time'],
            servings=request.POST['servings'],
        )
        for file in request.FILES.getlist('images'):
            RecipeImage.objects.create(recipe=recipe, image=file)
        messages.success(request, "Recipe published!")
        return redirect('accounts:chef_dashboard')

    return render(request, 'chef/create_recipe.html')


@login_required
def edit_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)

    if request.method == 'POST':
        recipe.title = request.POST['title']
        recipe.description = request.POST['description']
        recipe.prep_time = request.POST['prep_time']
        recipe.cook_time = request.POST['cook_time']
        recipe.servings = request.POST['servings']
        recipe.save()

        for file in request.FILES.getlist('images'):
            RecipeImage.objects.create(recipe=recipe, image=file)

        messages.success(request, "Recipe updated!")
        return redirect('accounts:chef_dashboard')

    return render(request, 'chef/create_recipe.html', {'recipe': recipe})


@login_required
def delete_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, "Recipe deleted")
        return redirect('accounts:chef_dashboard')
    return render(request, 'chef/delete_recipe.html', {'recipe': recipe})
def recipe_list(request):
    recipes = Recipe.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'recipes/list.html', {'recipes': recipes})
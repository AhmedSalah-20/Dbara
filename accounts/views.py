# accounts/views.py – VERSION FINALE CORRIGÉE & FONCTIONNELLE

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db import transaction
from django.conf import settings
import google.generativeai as genai
from .models import UserProfile, Recipe, RecipeImage


# ====================== BASIC VIEWS ======================
def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        try:
            if request.user.userprofile.role == 'chef':
                return redirect('accounts:chef_dashboard')
            elif request.user.userprofile.role == 'nutritionist':
                return redirect('accounts:nutritionist_dashboard')
        except UserProfile.DoesNotExist:
            pass
    return render(request, 'base/home.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role = request.POST.get('role', 'visitor')

        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas")
            return render(request, 'accounts/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris")
            return render(request, 'accounts/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé")
            return render(request, 'accounts/signup.html')

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password1)
            UserProfile.objects.create(user=user, role=role)
            login(request, user)
            messages.success(request, f"Bienvenue {username} !")

            if role == 'chef':
                return redirect('accounts:chef_dashboard')
            elif role == 'nutritionist':
                return redirect('accounts:nutritionist_dashboard')
            return redirect('accounts:home')

    return render(request, 'accounts/signup.html')


def login_view(request):
    if request.method == 'POST':
        identifier = request.POST['username'].strip()
        password = request.POST['password']

        user = authenticate(request, username=identifier, password=password)
        if not user:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if user:
            login(request, user)
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'visitor'})

            if user.is_staff:
                return redirect('/admin/')
            try:
                if user.userprofile.role == 'chef':
                    return redirect('accounts:chef_dashboard')
                elif user.userprofile.role == 'nutritionist':
                    return redirect('accounts:nutritionist_dashboard')
            except UserProfile.DoesNotExist:
                pass
            return redirect('accounts:home')
        else:
            messages.error(request, "Identifiants incorrects")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, "Déconnexion réussie")
    return redirect('accounts:home')


# ====================== CHEF DASHBOARD ======================
@login_required
def chef_dashboard(request):
    if request.user.is_staff:
        return redirect('/admin/')
    try:
        if request.user.userprofile.role != 'chef':
            messages.error(request, "Accès réservé aux chefs")
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
    try:
        if request.user.userprofile.role != 'chef':
            return redirect('accounts:home')
    except UserProfile.DoesNotExist:
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
        messages.success(request, "Recette publiée avec succès !")
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
        messages.success(request, "Recette modifiée !")
        return redirect('accounts:chef_dashboard')
    return render(request, 'chef/create_recipe.html', {'recipe': recipe})


@login_required
def delete_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, "Recette supprimée")
        return redirect('accounts:chef_dashboard')
    return render(request, 'chef/delete_recipe.html', {'recipe': recipe})


# ====================== NUTRITIONIST DASHBOARD ======================
@login_required
def nutritionist_dashboard(request):
    if request.user.is_staff:
        return redirect('/admin/')
    try:
        if request.user.userprofile.role != 'nutritionist':
            messages.error(request, "Accès réservé aux nutritionnistes")
            return redirect('accounts:home')
    except UserProfile.DoesNotExist:
        return redirect('accounts:home')

    all_recipes = Recipe.objects.filter(is_approved=True)
    total = all_recipes.count()
    healthy = all_recipes.filter(title__icontains="salade") | all_recipes.filter(title__icontains="poisson") | all_recipes.filter(title__icontains="légumes")

    context = {
        'total_recipes': total,
        'healthy_recipes': healthy.count(),
        'moderate_recipes': max(0, int(total * 0.4)),
        'unhealthy_recipes': max(0, total - healthy.count() - int(total * 0.4)),
    }
    return render(request, 'nutritionist/dashboard.html', context)


@login_required
def nutritionist_analyze(request):
    return render(request, 'nutritionist/analyze.html', {'title': 'Analyseur Nutritionnel'})


@login_required
def nutritionist_fiches(request):
    return render(request, 'nutritionist/fiches.html', {'title': 'Fiches Nutritionnelles'})


@login_required
def nutritionist_classification(request):
    return render(request, 'nutritionist/classification.html', {'title': 'Classement Santé'})


@login_required
def nutritionist_stats(request):
    return render(request, 'nutritionist/stats.html', {'title': 'Statistiques & Suivi'})


@login_required
def nutritionist_collaboration(request):
    return render(request, 'nutritionist/collaboration.html', {'title': 'Collaboration'})


# ====================== CHATBOT GEMINI – VERSION FONCTIONNELLE ======================
@login_required
def nutritionist_chatbot(request):
    try:
        if request.user.userprofile.role != 'nutritionist':
            messages.error(request, "Accès réservé aux nutritionnistes")
            return redirect('accounts:home')
    except AttributeError:
        return redirect('accounts:home')

    # Vérification de la clé
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        messages.error(request, "Clé API Gemini manquante dans le fichier .env")
        return render(request, 'nutritionist/chatbot.html', {'chat_history': []})

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3-flash-preview')

    chat_history = request.session.get('chat_history', [])

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if user_message:
            prompt = f"""
            Tu es le Dr. {request.user.username}, nutritionniste tunisien expert en cuisine traditionnelle.
            Réponds en français ou en arabe tunisien selon la langue de la question.
            Sois précis, détaillé et donne des conseils pratiques.
            Question : {user_message}
            """

            try:
                response = model.generate_content(prompt)
                bot_reply = response.text.strip() if response.text else "Je n'ai pas pu générer de réponse."

                chat_history.append({'user': user_message, 'bot': bot_reply})
            except Exception as e:
                error_msg = str(e)
                bot_reply = f"Erreur technique temporaire : {error_msg[:100]}..."
                chat_history.append({'user': user_message, 'bot': bot_reply})

            request.session['chat_history'] = chat_history[-30:]
            request.session.modified = True

    return render(request, 'nutritionist/chatbot.html', {
        'chat_history': chat_history
    })
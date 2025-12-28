# accounts/views.py – VERSION FINALE CORRIGÉE & FONCTIONNELLE
<<<<<<< HEAD
from django.core.mail import send_mail
=======

>>>>>>> b86e3f5426852e49c5b397d2b5702cb7885b4b02
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db import transaction
from django.conf import settings
import google.generativeai as genai
<<<<<<< HEAD
from .models import UserProfile, Recipe, RecipeImage, Comment, Rating, Favorite
=======
from .models import UserProfile, Recipe, RecipeImage
>>>>>>> b86e3f5426852e49c5b397d2b5702cb7885b4b02
from django.db import models

# ====================== BASIC VIEWS ======================
def home(request):
    # Redirections pour les utilisateurs connectés
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

    # 3 chefs les plus récemment inscrits
    recent_chefs = UserProfile.objects.filter(role='chef').select_related('user').order_by('-user__date_joined')[:3]
    for profile in recent_chefs:
        profile.recipe_count = profile.user.recipes.filter(is_approved=True).count()  # ← CORRIGÉ ICI

    # 3 recettes les plus récentes approuvées
    popular_recipes = Recipe.objects.filter(is_approved=True) \
        .select_related('author') \
        .prefetch_related('images') \
        .order_by('-created_at')[:3]

    context = {
        'recent_chefs': recent_chefs,
        'popular_recipes': popular_recipes,
    }
    return render(request, 'base/home.html', context)

def signup(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        role = request.POST.get('role', 'visitor')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'accounts/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'accounts/signup.html')

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password1)
<<<<<<< HEAD
            profile = UserProfile.objects.create(user=user, role=role)

=======

            profile = UserProfile.objects.create(user=user, role=role)

            # Pour Chef et Nutritionniste : compte désactivé jusqu'à approbation admin
>>>>>>> b86e3f5426852e49c5b397d2b5702cb7885b4b02
            if role in ['chef', 'nutritionist']:
                user.is_active = False
                user.save()

<<<<<<< HEAD
                # Pro fields...
                # (keep your existing code for chef/nutritionist here)

                profile.save()

                messages.success(request, "Your account has been created! Pending admin approval. You will receive an email when approved.")
                return redirect('accounts:login')

            else:
                # Visitor: immediate activation
                user.is_active = True
                user.save()

                # Optional fields for visitor
                profile.bio = request.POST.get('bio', '')
                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']

                profile.save()

                # Welcome email
                send_mail(
                    'Welcome to Dbara!',
                    f'Hello {username},\n\nThank you for joining Dbara!\n\nYou can now log in and enjoy the platform.\n\nBest regards,\nDbara Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                messages.success(request, "Your account has been created! Please log in.")
                return redirect('accounts:login')  # Redirection to login
=======
                # Champs communs aux pros
                profile.region = request.POST.get('region', '')
                profile.years_experience = request.POST.get('years_experience') or None
                profile.bio = request.POST.get('bio', '')

                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']
                if 'certificate' in request.FILES:
                    profile.certificate = request.FILES['certificate']

                # Speciality uniquement pour les chefs
                if role == 'chef':
                    profile.speciality = request.POST.get('speciality', '')

                profile.save()

                messages.success(request, 
                    "Your nutritionist account has been created and is pending admin approval. "
                    "You will receive an email when your account is activated.")
                return redirect('accounts:login')

            else:
                # Visiteur : compte actif immédiatement
                login(request, user)
                messages.success(request, f"Welcome {username}! Your account is ready.")
                return redirect('accounts:home')
>>>>>>> b86e3f5426852e49c5b397d2b5702cb7885b4b02

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

<<<<<<< HEAD
        if user and user.is_active:
            login(request, user)

            # ADMIN goes to Django admin
            if user.is_staff or user.is_superuser:
                return redirect('/admin/')

            # Normal users go to their role dashboard
            try:
                profile = user.userprofile
                if profile.role == 'chef':
                    return redirect('accounts:chef_dashboard')
                elif profile.role == 'nutritionist':
                    return redirect('accounts:nutritionist_dashboard')
                elif profile.role == 'visitor':
                    return redirect('accounts:visitor_dashboard')
            except UserProfile.DoesNotExist:
                pass

            return redirect('accounts:home')
        else:
            messages.error(request, "Invalid credentials or account pending approval.")

    return render(request, 'accounts/login.html')

=======
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


>>>>>>> b86e3f5426852e49c5b397d2b5702cb7885b4b02
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
def edit_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('accounts:home')

    # Autorise chefs ET nutritionnistes
    if profile.role not in ['chef', 'nutritionist']:
        messages.error(request, "Access restricted to professional accounts.")
        return redirect('accounts:home')

    if request.method == 'POST':
        # Mise à jour User
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if username and username != request.user.username:
            if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
                messages.error(request, "This username is already taken.")
                return render(request, 'chef/edit_profile.html', {'profile': profile})
            request.user.username = username

        if email and email != request.user.email:
            if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                messages.error(request, "This email is already registered.")
                return render(request, 'chef/edit_profile.html', {'profile': profile})
            request.user.email = email

        if password:
            request.user.set_password(password)
            messages.info(request, "Your password has been updated. Please log in again.")
            return redirect('accounts:logout')

        request.user.save()

        # Mise à jour Profile
        profile.bio = request.POST.get('bio', profile.bio)
        profile.region = request.POST.get('region', profile.region)
        profile.years_experience = request.POST.get('years_experience') or None

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']
        if 'certificate' in request.FILES:
            profile.certificate = request.FILES['certificate']

        # Speciality seulement pour les chefs
        if profile.role == 'chef':
            profile.speciality = request.POST.get('speciality', profile.speciality)

        profile.save()

        messages.success(request, "Your profile has been updated successfully!")
        return redirect('accounts:chef_dashboard')  # ou nutritionist_dashboard si tu en as un

    context = {
        'profile': profile,
    }
    return render(request, 'chef/edit_profile.html', context)

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
# ====================== PAGES PUBLIQUES ======================

def chefs_list(request):
    chefs = UserProfile.objects.filter(role='chef').select_related('user')
    for profile in chefs:
        profile.recipe_count = profile.user.recipes.filter(is_approved=True).count()

    # Profil de l'utilisateur connecté pour la navbar
    current_profile = None
    if request.user.is_authenticated:
        try:
            current_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            current_profile = None

    context = {
        'chefs': chefs,
        'page_title': 'Nos Chefs Tunisiens 🔥',
        'current_profile': current_profile,  # ← IMPORTANT
    }
    return render(request, 'public/chefs_list.html', context)


def nutritionists_list(request):
    nutritionists = UserProfile.objects.filter(role='nutritionist').select_related('user')
    context = {
        'nutritionists': nutritionists,
        'page_title': 'Nos Nutritionnistes 🥗'
    }
    return render(request, 'public/nutritionists_list.html', context)


def public_recipes(request):
    recipes = Recipe.objects.filter(is_approved=True).select_related('author').prefetch_related('images').order_by('-created_at')
    context = {
        'recipes': recipes,
        'page_title': 'Toutes les Recettes Tunisiennes'
    }
    return render(request, 'public/recipes_list.html', context)



def search_recipes(request):
    query = request.GET.get('q', '').strip()
    
    recipes = []
    chefs = []
    nutritionists = []

    if query:
        # Recherche dans les recettes (titre ou description)
        recipes = Recipe.objects.filter(is_approved=True) \
            .filter(models.Q(title__icontains=query) | models.Q(description__icontains=query)) \
            .select_related('author') \
            .prefetch_related('images') \
            .order_by('-created_at')

        # Recherche dans les chefs (nom d'utilisateur)
        chefs = UserProfile.objects.filter(role='chef') \
            .filter(user__username__icontains=query) \
            .select_related('user')

        # Recherche dans les nutritionnistes
        nutritionists = UserProfile.objects.filter(role='nutritionist') \
            .filter(user__username__icontains=query) \
            .select_related('user')

        # Ajoute le nombre de recettes pour les chefs trouvés
        for profile in chefs:
            profile.recipe_count = profile.user.recipes.filter(is_approved=True).count()

    context = {
        'query': query,
        'recipes': recipes,
        'chefs': chefs,
        'nutritionists': nutritionists,
        'has_results': bool(recipes or chefs or nutritionists),
    }
    return render(request, 'public/search_results.html', context)


def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, is_approved=True)

    # Clé unique pour cette recette et cette session/utilisateur
    view_key = f"recipe_viewed_{recipe.pk}"

    # Cas 1 : Le chef voit sa propre recette → pas de vue comptée
    if request.user.is_authenticated and request.user == recipe.author:
        has_viewed = True

    # Cas 2 : Utilisateur connecté (nutritionniste, visiteur connecté)
    elif request.user.is_authenticated:
        has_viewed = request.session.get(view_key, False)
        if not has_viewed:
            request.session[view_key] = True

    # Cas 3 : Visiteur non connecté → on utilise la session anonyme
    else:
        has_viewed = request.session.get(view_key, False)
        if not has_viewed:
            request.session[view_key] = True

    # On incrémente la vue seulement si ce n'est pas déjà compté
    if not has_viewed:
        recipe.views += 1
        recipe.save(update_fields=['views'])

    context = {
        'recipe': recipe,
    }
    return render(request, 'public/recipe_detail.html', context)


def chef_profile_detail(request, username):
    profile = get_object_or_404(UserProfile, user__username=username, role='chef')
    recipes = Recipe.objects.filter(author=profile.user, is_approved=True) \
        .prefetch_related('images') \
        .order_by('-created_at')
    
    context = {
        'chef_profile': profile,
        'recipes': recipes,
        'recipe_count': recipes.count(),
    }
    return render(request, 'public/chef_profile_detail.html', context)


def chef_recipes(request, username):
    profile = get_object_or_404(UserProfile, user__username=username, role='chef')
    recipes = Recipe.objects.filter(author=profile.user, is_approved=True) \
        .prefetch_related('images') \
        .order_by('-created_at')
    
    context = {
        'chef_profile': profile,
        'recipes': recipes,
    }
<<<<<<< HEAD
    return render(request, 'public/chef_recipes.html', context)


@login_required
def visitor_dashboard(request):
    if request.user.userprofile.role != 'visitor':
        messages.error(request, "Access restricted to visitors.")
        return redirect('accounts:home')

    favorites = Favorite.objects.filter(user=request.user).select_related('recipe', 'recipe__author')
    context = {
        'favorites': favorites,
    }
    return render(request, 'visitor/dashboard.html', context)


# Add Comment
@login_required
def add_comment(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, is_approved=True)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(recipe=recipe, author=request.user, content=content)
            messages.success(request, "Comment added!")
    return redirect('accounts:recipe_detail', pk=pk)

# Add Rating
@login_required
def add_rating(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, is_approved=True)
    if request.method == 'POST':
        score = request.POST.get('score')
        if score and score.isdigit():
            score = int(score)
            if 1 <= score <= 5:
                Rating.objects.update_or_create(recipe=recipe, author=request.user, defaults={'score': score})
                messages.success(request, "Rating added!")
    return redirect('accounts:recipe_detail', pk=pk)

# Toggle Favorite
@login_required
def toggle_favorite(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, is_approved=True)
    fav, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
    if not created:
        fav.delete()
        messages.info(request, "Removed from favorites")
    else:
        messages.success(request, "Added to favorites")
    return redirect('accounts:recipe_detail', pk=pk)

# Favorites List
@login_required
def favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('recipe')
    return render(request, 'visitor/favorites.html', {'favorites': favorites})

# Chatbot
@login_required
def chatbot(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        # Here, integrate Gemini code from previous
        # ... (add your Gemini code here)

    return render(request, 'visitor/chatbot.html')
=======
    return render(request, 'public/chef_recipes.html', context)
>>>>>>> b86e3f5426852e49c5b397d2b5702cb7885b4b02

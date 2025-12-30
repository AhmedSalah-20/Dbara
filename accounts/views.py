# accounts/views.py – VERSION FINALE COMPLÈTE & SÉCURISÉE

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Q as models_Q
from django.db import transaction
from django.conf import settings
from django.core.mail import send_mail
from django.views.decorators.cache import never_cache
from .models import UserProfile, Recipe, RecipeImage, Comment, Rating, Favorite, Notification
from django.urls import reverse
import google.generativeai as genai
from django.db.models import Avg


# ====================== BASIC VIEWS ======================
def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/admin/')
        try:
            profile = request.user.userprofile
            if profile.role == 'chef':
                return redirect('accounts:chef_dashboard')
            elif profile.role == 'nutritionist':
                return redirect('accounts:nutritionist_dashboard')
            elif profile.role == 'visitor':
                return redirect('accounts:visitor_dashboard')
        except UserProfile.DoesNotExist:
            pass

    recent_chefs = UserProfile.objects.filter(role='chef').select_related('user').order_by('-user__date_joined')[:3]
    for profile in recent_chefs:
        profile.recipe_count = profile.user.recipes.filter(is_approved=True).count()

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
            profile = UserProfile.objects.create(user=user, role=role)

            if role in ['chef', 'nutritionist']:
                user.is_active = False
                user.save()

                profile.region = request.POST.get('region', '')
                profile.years_experience = request.POST.get('years_experience') or None
                profile.bio = request.POST.get('bio', '')

                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']
                if 'certificate' in request.FILES:
                    profile.certificate = request.FILES['certificate']

                if role == 'chef':
                    profile.speciality = request.POST.get('speciality', '')

                profile.save()

                messages.success(request, "Your professional account has been created! Pending admin approval.")
                return redirect('accounts:login')

            else:
                user.is_active = True
                user.save()

                profile.bio = request.POST.get('bio', '')
                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']

                profile.save()

                send_mail(
                    'Welcome to Dbara!',
                    f'Hello {username},\n\nThank you for joining Dbara!\n\nYou can now log in and explore Tunisian recipes.\n\nBest regards,\nDbara Team',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                messages.success(request, "Your account has been created! Please log in.")
                return redirect('accounts:login')

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

        if user and user.is_active:
            login(request, user)

            if user.is_staff or user.is_superuser:
                return redirect('/admin/')

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


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    response = redirect('accounts:login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# ====================== PROTECTED VIEWS WITH @never_cache ======================
@never_cache
@login_required
def visitor_dashboard(request):
    if request.user.userprofile.role != 'visitor':
        messages.error(request, "Access restricted to visitors.")
        return redirect('accounts:home')

    favorites = Favorite.objects.filter(user=request.user).select_related('recipe', 'recipe__author')
    context = {'favorites': favorites}
    return render(request, 'visitor/dashboard.html', context)


@never_cache
@login_required
def chef_dashboard(request):
    if request.user.userprofile.role != 'chef':
        messages.error(request, "Access restricted to chefs.")
        return redirect('accounts:home')

    recipes = Recipe.objects.filter(author=request.user).order_by('-created_at')
    total_views = recipes.aggregate(total=Sum('views'))['total'] or 0

    context = {
        'recipes': recipes,
        'total_recipes': recipes.count(),
        'total_views': total_views,
    }
    return render(request, 'chef/dashboard.html', context)


@never_cache
@login_required
def nutritionist_dashboard(request):
    if request.user.userprofile.role != 'nutritionist':
        messages.error(request, "Access restricted to nutritionists.")
        return redirect('accounts:home')

    context = {}
    return render(request, 'nutritionist/dashboard.html', context)


@never_cache
@login_required
def edit_profile(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, "Profile not found.")
        return redirect('accounts:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if username and username != request.user.username:
            if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
                messages.error(request, "Username already taken.")
                return render(request, 'chef/edit_profile.html', {'profile': profile})
            request.user.username = username

        if email and email != request.user.email:
            if User.objects.filter(email=email).exclude(pk=request.user.pk).exists():
                messages.error(request, "Email already registered.")
                return render(request, 'chef/edit_profile.html', {'profile': profile})
            request.user.email = email

        if password:
            request.user.set_password(password)
            messages.info(request, "Password updated. Please log in again.")
            return redirect('accounts:logout')

        request.user.save()

        profile.bio = request.POST.get('bio', profile.bio)
        profile.region = request.POST.get('region', profile.region)
        profile.years_experience = request.POST.get('years_experience') or None

        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        if profile.role in ['chef', 'nutritionist'] and 'certificate' in request.FILES:
            profile.certificate = request.FILES['certificate']

        if profile.role == 'chef':
            profile.speciality = request.POST.get('speciality', profile.speciality)

        profile.save()

        messages.success(request, "Profile updated successfully!")
        if profile.role == 'visitor':
            return redirect('accounts:visitor_dashboard')
        elif profile.role == 'chef':
            return redirect('accounts:chef_dashboard')
        else:
            return redirect('accounts:nutritionist_dashboard')

    return render(request, 'chef/edit_profile.html', {'profile': profile})


@never_cache
@login_required
def favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('recipe', 'recipe__author')
    return render(request, 'visitor/favorites.html', {'favorites': favorites})


@never_cache
@login_required
def chatbot(request):
    return render(request, 'visitor/chatbot.html')


# ====================== CHEF RECIPE ACTIONS ======================
@never_cache
@login_required
def create_recipe(request):
    if request.user.userprofile.role != 'chef':
        messages.error(request, "Access restricted to chefs.")
        return redirect('accounts:home')

    if request.method == 'POST':
        recipe = Recipe.objects.create(
            author=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            prep_time=request.POST['prep_time'],
            cook_time=request.POST['cook_time'],
            servings=request.POST['servings'],
            ingredients=request.POST.get('ingredients', ''),
            steps=request.POST.get('steps', ''),
        )
        for file in request.FILES.getlist('images'):
            RecipeImage.objects.create(recipe=recipe, image=file)
        messages.success(request, "Recipe created successfully!")
        return redirect('accounts:chef_dashboard')

    return render(request, 'chef/create_recipe.html')


@never_cache
@login_required
def edit_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
    if request.method == 'POST':
        recipe.title = request.POST['title']
        recipe.description = request.POST['description']
        recipe.prep_time = request.POST['prep_time']
        recipe.cook_time = request.POST['cook_time']
        recipe.servings = request.POST['servings']
        recipe.ingredients = request.POST.get('ingredients', recipe.ingredients)
        recipe.steps = request.POST.get('steps', recipe.steps)
        recipe.save()
        for file in request.FILES.getlist('images'):
            RecipeImage.objects.create(recipe=recipe, image=file)
        messages.success(request, "Recipe updated!")
        return redirect('accounts:chef_dashboard')

    context = {'recipe': recipe}
    return render(request, 'chef/create_recipe.html', context)


@never_cache
@login_required
def delete_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, "Recipe deleted.")
        return redirect('accounts:chef_dashboard')
    return render(request, 'chef/delete_recipe.html', {'recipe': recipe})


# ====================== NUTRITIONIST PAGES ======================
@never_cache
@login_required
def nutritionist_analyze(request):
    if request.user.userprofile.role != 'nutritionist':
        messages.error(request, "Access restricted to nutritionists.")
        return redirect('accounts:home')
    return render(request, 'nutritionist/analyze.html')


@never_cache
@login_required
def nutritionist_fiches(request):
    if request.user.userprofile.role != 'nutritionist':
        messages.error(request, "Access restricted to nutritionists.")
        return redirect('accounts:home')
    return render(request, 'nutritionist/fiches.html')


@never_cache
@login_required
def nutritionist_classification(request):
    if request.user.userprofile.role != 'nutritionist':
        messages.error(request, "Access restricted to nutritionists.")
        return redirect('accounts:home')
    return render(request, 'nutritionist/classification.html')


@never_cache
@login_required
def nutritionist_stats(request):
    if request.user.userprofile.role != 'nutritionist':
        messages.error(request, "Access restricted to nutritionists.")
        return redirect('accounts:home')
    return render(request, 'nutritionist/stats.html')


@never_cache
@login_required
def nutritionist_collaboration(request):
    if request.user.userprofile.role != 'nutritionist':
        messages.error(request, "Access restricted to nutritionists.")
        return redirect('accounts:home')
    return render(request, 'nutritionist/collaboration.html')


# ====================== PUBLIC VIEWS ======================
def chefs_list(request):
    chefs = UserProfile.objects.filter(role='chef').select_related('user')
    for profile in chefs:
        profile.recipe_count = profile.user.recipes.filter(is_approved=True).count()

    context = {'chefs': chefs, 'page_title': 'Our Tunisian Chefs 🔥'}
    return render(request, 'public/chefs_list.html', context)


def nutritionists_list(request):
    nutritionists = UserProfile.objects.filter(role='nutritionist').select_related('user')
    context = {'nutritionists': nutritionists, 'page_title': 'Our Nutritionists 🥗'}
    return render(request, 'public/nutritionists_list.html', context)


def public_recipes(request):
    recipes = Recipe.objects.filter(is_approved=True).select_related('author').prefetch_related('images').order_by('-created_at')
    context = {'recipes': recipes, 'page_title': 'All Tunisian Recipes'}
    return render(request, 'public/recipes_list.html', context)


def search_recipes(request):
    query = request.GET.get('q', '').strip()
    recipes = []
    chefs = []
    nutritionists = []

    if query:
        recipes = Recipe.objects.filter(is_approved=True) \
            .filter(models_Q(title__icontains=query) | models_Q(description__icontains=query)) \
            .select_related('author') \
            .prefetch_related('images') \
            .order_by('-created_at')

        chefs = UserProfile.objects.filter(role='chef', user__username__icontains=query).select_related('user')
        nutritionists = UserProfile.objects.filter(role='nutritionist', user__username__icontains=query).select_related('user')

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

    # Smart view counter
    view_key = f"recipe_viewed_{recipe.pk}"
    has_viewed = False

    if request.user.is_authenticated and request.user == recipe.author:
        has_viewed = True
    elif request.user.is_authenticated:
        has_viewed = request.session.get(view_key, False)
        if not has_viewed:
            request.session[view_key] = True
    else:
        has_viewed = request.session.get(view_key, False)
        if not has_viewed:
            request.session[view_key] = True

    # Increment view count only if not already viewed
    if not has_viewed:
        recipe.views += 1
        recipe.save(update_fields=['views'])

    # Calculate average rating and count – ALWAYS (even if no new view)
    rating_agg = recipe.ratings.aggregate(avg=Avg('score'))
    avg_rating = rating_agg['avg'] if rating_agg['avg'] is not None else 0.0
    rating_count = recipe.ratings.count()
    # All individual ratings with author
    individual_ratings = recipe.ratings.select_related('author').order_by('-created_at')

    context = {
        'recipe': recipe,
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'individual_ratings': individual_ratings,
    }
    return render(request, 'public/recipe_detail.html', context)

def chef_profile_detail(request, username):
    profile = get_object_or_404(UserProfile, user__username=username, role='chef')
    recipes = Recipe.objects.filter(author=profile.user, is_approved=True).prefetch_related('images').order_by('-created_at')
    context = {'chef_profile': profile, 'recipes': recipes, 'recipe_count': recipes.count()}
    return render(request, 'public/chef_profile_detail.html', context)


def chef_recipes(request, username):
    profile = get_object_or_404(UserProfile, user__username=username, role='chef')
    recipes = Recipe.objects.filter(author=profile.user, is_approved=True).prefetch_related('images').order_by('-created_at')
    context = {'chef_profile': profile, 'recipes': recipes}
    return render(request, 'public/chef_recipes.html', context)


# ====================== VISITOR FEATURES ======================
@never_cache
@login_required
def add_comment(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, is_approved=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent')
        if content:
            parent = None
            if parent_id:
                parent = get_object_or_404(Comment, pk=parent_id, recipe=recipe)

            comment = Comment.objects.create(
                recipe=recipe,
                author=request.user,
                content=content,
                parent=parent
            )

            # Notification pour le Chef (seulement si c'est un Visiteur qui commente)
            if request.user.userprofile.role == 'visitor':
                Notification.objects.create(
                    user=recipe.author,
                    message=f"{request.user.username} a commenté votre recette '{recipe.title}'",
                    link=reverse('accounts:recipe_detail', args=[recipe.pk]) + '#comments-section'
                )

            # Si c'est une réponse → notification pour l'auteur du commentaire parent (Visiteur)
            if parent and parent.author != recipe.author:  # évite d'envoyer au Chef s'il répond
                Notification.objects.create(
                    user=parent.author,
                    message=f"Le Chef {recipe.author.username} a répondu à votre commentaire sur '{recipe.title}'",
                    link=reverse('accounts:recipe_detail', args=[recipe.pk]) + '#comments-section'
                )

            messages.success(request, "Commentaire ajouté !")
        return redirect('accounts:recipe_detail', pk=pk)

    return redirect('accounts:recipe_detail', pk=pk)

@never_cache
@login_required
def add_rating(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, is_approved=True)
    if request.user == recipe.author:
        messages.error(request, "Vous ne pouvez pas noter votre propre recette.")
        return redirect('accounts:recipe_detail', pk=pk)

    if request.method == 'POST':
        score = request.POST.get('score')
        if score and score.isdigit():
            score = int(score)
            if 1 <= score <= 5:
                Rating.objects.update_or_create(
                    recipe=recipe,
                    author=request.user,
                    defaults={'score': score}
                )

                # Notification pour le Chef (nouvelle note)
                Notification.objects.create(
                    user=recipe.author,
                    message=f"{request.user.username} a noté votre recette '{recipe.title}' : {score}/5 ⭐",
                    link=reverse('accounts:recipe_detail', args=[recipe.pk]) + '#ratings-section'
                )

                messages.success(request, "Note ajoutée !")
    return redirect('accounts:recipe_detail', pk=pk)

@never_cache
@login_required
def toggle_favorite(request, pk):
    # Favoris réservés aux Visiteurs seulement
    if request.user.userprofile.role != 'visitor':
        messages.error(request, "This feature is only for visitors.")
        return redirect('accounts:recipe_detail', pk=pk)

    recipe = get_object_or_404(Recipe, pk=pk, is_approved=True)

    fav, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
    
    if not created:
        fav.delete()
        messages.info(request, "Removed from favorites ❤️")
    else:
        messages.success(request, "Added to favorites 🤍")

    # Redirection intelligente selon la page d'origine
    referer = request.META.get('HTTP_REFERER', '')

    if 'favorites' in referer or request.path == '/favorites/':
        # Si on vient de My Favorites → reste sur le dashboard
        return redirect('accounts:favorites')
    elif referer:
        # Sinon, retourne à la page précédente (liste ou détail)
        return redirect(referer)
    else:
        # Fallback
        return redirect('accounts:public_recipes')

@never_cache
@login_required
def nutritionist_chatbot(request):
    if request.user.userprofile.role != 'nutritionist':
        messages.error(request, "Access restricted to nutritionists.")
        return redirect('accounts:home')

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        messages.error(request, "Gemini API key missing.")
        return render(request, 'nutritionist/chatbot.html', {'chat_history': []})

    genai.configure(api_key=api_key)

    # Current working model in December 2025
    model = genai.GenerativeModel("gemini-2.5-flash")

    chat_history = request.session.get('chat_history', [])

    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()
        if user_message:
            prompt = f"""
            You are Dr. {request.user.username}, a Tunisian nutritionist expert in traditional cuisine.
            Answer in French or Tunisian Arabic based on the question's language.
            Be precise, detailed, and give practical advice.
            Question: {user_message}
            """

            try:
                response = model.generate_content(prompt)
                bot_reply = response.text.strip() if response.text else "I couldn't generate a response."

                chat_history.append({'user': user_message, 'bot': bot_reply})
            except Exception as e:
                bot_reply = f"Technical error: {str(e)[:100]}..."
                chat_history.append({'user': user_message, 'bot': bot_reply})

            request.session['chat_history'] = chat_history[-30:]
            request.session.modified = True

    return render(request, 'nutritionist/chatbot.html', {'chat_history': chat_history})




@never_cache
@login_required

def mark_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect(request.META.get('HTTP_REFERER', request.path))

@never_cache
@login_required
def read_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect(notif.link or 'accounts:visitor_dashboard')


@never_cache
@login_required
def notifications(request):
    notifications = request.user.notifications.all()
    return render(request, 'accounts/notifications.html', {'notifications': notifications})
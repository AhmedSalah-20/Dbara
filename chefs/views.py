from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Recipe, RecipeImage

@login_required
def create_recipe(request):
    if request.user.profile.role != 'chef':
        messages.error(request, "Only chefs can create recipes.")
        return redirect('accounts:home')

    if request.method == 'POST':
        recipe = Recipe.objects.create(
            author=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            prep_time=request.POST['prep_time'],
            cook_time=request.POST['cook_time'],
            servings=request.POST['servings']
        )
        
        for img in request.FILES.getlist('images'):
            RecipeImage.objects.create(recipe=recipe, image=img)
            
        messages.success(request, f"Recipe '{recipe.title}' published successfully!")
        return redirect('chefs:dashboard')

    return render(request, 'chefs/create_recipe.html')
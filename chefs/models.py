# chefs/models.py
from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('entree', 'Entrée'),
        ('plat', 'Plat principal'),
        ('dessert', 'Dessert'),
        ('boisson', 'Boisson'),
        ('autre', 'Autre'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField(help_text="Séparez les ingrédients par des virgules ou des sauts de ligne")
    instructions = models.TextField()
    prep_time = models.PositiveIntegerField(help_text="En minutes", blank=True, null=True)
    cook_time = models.PositiveIntegerField(help_text="En minutes", blank=True, null=True)
    servings = models.PositiveIntegerField(default=4)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='plat')

    chef = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    is_published = models.BooleanField(default=False)  # Admin doit valider
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='recipes/')
    caption = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)  # image principale

    def save(self, *args, **kwargs):
        if self.is_main:
            # Une seule image principale par recette
            RecipeImage.objects.filter(recipe=self.recipe, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)
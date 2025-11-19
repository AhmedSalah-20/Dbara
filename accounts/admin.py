# accounts/admin.py
from django.contrib import admin
from .models import UserProfile, Recipe, RecipeImage

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_editable = ('role',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_approved', 'views')
    list_filter = ('is_approved', 'created_at')
    list_editable = ('is_approved',)

@admin.register(RecipeImage)
class RecipeImageAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'image')
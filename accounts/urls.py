# accounts/urls.py   ← REPLACE ALL WITH THIS

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Basic pages
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # CHEF DASHBOARD - NEW CLEAN URLs
    path('chef/dashboard/', views.chef_dashboard, name='chef_dashboard'),
    path('chef/recipes/create/', views.create_recipe, name='create_recipe'),
    path('chef/recipes/<int:pk>/edit/', views.edit_recipe, name='edit_recipe'),      # ← CHANGED from modify_recipe
    path('chef/recipes/<int:pk>/delete/', views.delete_recipe, name='delete_recipe'),

        # NUTRITIONNIST DASHBOARD
    path('nutritionist/dashboard/', views.nutritionist_dashboard, name='nutritionist_dashboard'),
    path('nutritionist/analyze/', views.nutritionist_analyze, name='nutritionist_analyze'),
    path('nutritionist/fiches/', views.nutritionist_fiches, name='nutritionist_fiches'),
    path('nutritionist/classification/', views.nutritionist_classification, name='nutritionist_classification'),
    path('nutritionist/chatbot/', views.nutritionist_chatbot, name='nutritionist_chatbot'),
    path('nutritionist/stats/', views.nutritionist_stats, name='nutritionist_stats'),
    path('nutritionist/collaboration/', views.nutritionist_collaboration, name='nutritionist_collaboration'),

    # PAGES PUBLIQUES – AJOUTÉES ICI
    path('chefs/', views.chefs_list, name='chefs_list'),
    path('nutritionists/', views.nutritionists_list, name='nutritionists_list'),
    path('recipes/', views.public_recipes, name='public_recipes'),
]
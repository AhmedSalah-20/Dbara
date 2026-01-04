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

    path('chef/profile/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.search_recipes, name='search_recipes'),

    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),


    path('chef/<str:username>/', views.chef_profile_detail, name='chef_profile_detail'),
    path('chef/<str:username>/recipes/', views.chef_recipes, name='chef_recipes'),

path('visitor/dashboard/', views.visitor_dashboard, name='visitor_dashboard'),
path('add_comment/<int:pk>/', views.add_comment, name='add_comment'),
path('add_rating/<int:pk>/', views.add_rating, name='add_rating'),
path('toggle_favorite/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
path('favorites/', views.favorites, name='favorites'),
path('chatbot/', views.chatbot, name='chatbot'),

path('mark-notifications-read/', views.mark_notifications_read, name='mark_notifications_read'),

path('notification/<int:notif_id>/read/', views.read_notification, name='read_notification'),


path('notifications/', views.notifications, name='notifications'),

path('analyze/', views.nutritionist_analyze, name='nutritionist_analyze'),
path('analyze/<int:pk>/', views.analyze_recipe, name='analyze_recipe'),


path('fiches/', views.nutritionist_fiches, name='nutritionist_fiches'),
path('fiches/create/', views.create_nutrition_sheet, name='create_nutrition_sheet'),
path('fiches/<int:pk>/edit/', views.edit_nutrition_sheet, name='edit_nutrition_sheet'),
path('fiches/<int:pk>/delete/', views.delete_nutrition_sheet, name='delete_nutrition_sheet'),

path('nutrition-library/', views.public_nutrition_library, name='public_nutrition_library'),
path('nutrition-sheet/<int:pk>/', views.public_nutrition_sheet_detail, name='public_nutrition_sheet_detail'),
path('nutritionist/<int:user_id>/sheets/', views.nutritionist_sheets, name='nutritionist_sheets'),

]
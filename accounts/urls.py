# accounts/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Basic pages
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Admin Dashboard (personnalisé)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/delete-comment/<int:comment_id>/', views.admin_delete_comment, name='admin_delete_comment'),

    # Chef Dashboard
    path('chef/dashboard/', views.chef_dashboard, name='chef_dashboard'),
    path('chef/recipes/create/', views.create_recipe, name='create_recipe'),
    path('chef/recipes/<int:pk>/edit/', views.edit_recipe, name='edit_recipe'),
    path('chef/recipes/<int:pk>/delete/', views.delete_recipe, name='delete_recipe'),

    # Nutritionist Dashboard
    path('nutritionist/dashboard/', views.nutritionist_dashboard, name='nutritionist_dashboard'),
    path('nutritionist/analyze/', views.nutritionist_analyze, name='nutritionist_analyze'),
    path('nutritionist/fiches/', views.nutritionist_fiches, name='nutritionist_fiches'),
    path('nutritionist/stats/', views.nutritionist_stats, name='nutritionist_stats'),
    path('nutritionist/collaboration/', views.nutritionist_collaboration, name='nutritionist_collaboration'),

    # Visitor Dashboard
    path('visitor/dashboard/', views.visitor_dashboard, name='visitor_dashboard'),
    path('discussions/', views.visitor_discussions, name='visitor_discussions'),

    # Public pages
    path('chefs/', views.chefs_list, name='chefs_list'),
    path('nutritionists/', views.nutritionists_list, name='nutritionists_list'),
    path('recipes/', views.public_recipes, name='public_recipes'),
    path('search/', views.search_recipes, name='search_recipes'),

    # Recipe detail & actions
    path('recipe/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('add_comment/<int:pk>/', views.add_comment, name='add_comment'),
    path('add_rating/<int:pk>/', views.add_rating, name='add_rating'),
    path('toggle_favorite/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorites, name='favorites'),

    # Profile
    path('chef/profile/edit/', views.edit_profile, name='edit_profile'),
    path('chef/<str:username>/', views.chef_profile_detail, name='chef_profile_detail'),
    path('chef/<str:username>/recipes/', views.chef_recipes, name='chef_recipes'),

    # Notifications
    path('mark-notifications-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('notification/<int:notif_id>/read/', views.read_notification, name='read_notification'),
    path('notifications/', views.notifications, name='notifications'),

    # Nutritionist analysis & fiches
    path('analyze/<int:pk>/', views.analyze_recipe, name='analyze_recipe'),
    path('fiches/create/', views.create_nutrition_sheet, name='create_nutrition_sheet'),
    path('fiches/<int:pk>/edit/', views.edit_nutrition_sheet, name='edit_nutrition_sheet'),
    path('fiches/<int:pk>/delete/', views.delete_nutrition_sheet, name='delete_nutrition_sheet'),

    # Public nutrition library
    path('nutrition-library/', views.public_nutrition_library, name='public_nutrition_library'),
    path('nutrition-sheet/<int:pk>/', views.public_nutrition_sheet_detail, name='public_nutrition_sheet_detail'),
    path('nutritionist/<int:user_id>/sheets/', views.nutritionist_sheets, name='nutritionist_sheets'),

    # Messaging
    path('send-message/<int:recipient_id>/', views.send_nutrition_message, name='send_nutrition_message'),
    path('reply-message/<int:message_id>/', views.reply_nutrition_message, name='reply_nutrition_message'),
    path('visitor-reply/<int:message_id>/', views.visitor_reply_message, name='visitor_reply_message'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),

    # Chatbot public (unique pour tous)
    path('chatbot/', views.public_chatbot, name='public_chatbot'),


  path('admin-dashboard/manage-users/', views.admin_manage_users, name='admin_manage_users'),
path('admin-dashboard/edit-user/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
path('admin-dashboard/delete-user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
path('admin-dashboard/approve-professional/<int:user_id>/', views.admin_approve_professional, name='admin_approve_professional'),
path('admin-dashboard/add-user/', views.admin_add_user, name='admin_add_user'),


path('admin-dashboard/manage-recipes/', views.admin_manage_recipes, name='admin_manage_recipes'),
]
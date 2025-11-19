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
]
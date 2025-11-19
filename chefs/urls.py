# chefs/urls.py
from django.urls import path
from . import views

app_name = 'chefs'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('recipe/create/', views.create_recipe, name='create_recipe'),
    path('recipe/<int:pk>/edit/', views.edit_recipe, name='edit_recipe'),
    path('recipe/<int:pk>/delete/', views.delete_recipe, name='delete_recipe'),
]
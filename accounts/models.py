# accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('chef', 'Chef'),
        ('nutritionist', 'Nutritionniste'),
        ('visitor', 'Visiteur'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='visitor')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    def is_chef(self):
        return self.role == 'chef'

    def is_nutritionist(self):
        return self.role == 'nutritionist'

class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    prep_time = models.PositiveIntegerField(help_text="En minutes")
    cook_time = models.PositiveIntegerField(help_text="En minutes")
    servings = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)

    is_approved = models.BooleanField(default=False)  # ← Add this line
    def __str__(self):
        return self.title

class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='recipes/')
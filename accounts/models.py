# accounts/models.py
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('visitor', 'Visitor'),
        ('chef', 'Chef'),
        ('nutritionist', 'Nutritionist'),
    )

    SPECIALITY_CHOICES = (
        ('traditional', 'Traditional Tunisian'),
        ('seafood', 'Seafood Specialist'),
        ('pastry', 'Pastry & Desserts'),
        ('grill', 'Grill & BBQ'),
        ('vegetarian', 'Vegetarian & Healthy'),
        ('fusion', 'Modern Fusion'),
        ('other', 'Other'),
    )

    REGION_CHOICES = (
        ('tunis', 'Tunis'),
        ('ariana', 'Ariana'),
        ('sfax', 'Sfax'),
        ('sousse', 'Sousse'),
        ('monastir', 'Monastir'),
        ('bizerte', 'Bizerte'),
        ('nabeul', 'Nabeul'),
        ('other', 'Other Region'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='visitor')

    # Chef profile fields
    profile_picture = models.ImageField(upload_to='chefs/profiles/', blank=True, null=True)
    certificate = models.FileField(upload_to='chefs/certificates/', blank=True, null=True,
                                   help_text="Upload your culinary certificate (PDF or image) - required for verification")
    speciality = models.CharField(max_length=50, choices=SPECIALITY_CHOICES, blank=True)
    region = models.CharField(max_length=50, choices=REGION_CHOICES, blank=True)
    years_experience = models.PositiveIntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True, help_text="Tell us about your culinary journey")

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def is_chef(self):
        return self.role == 'chef'

    def is_nutritionist(self):
        return self.role == 'nutritionist'


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    prep_time = models.PositiveIntegerField(help_text="In minutes")
    cook_time = models.PositiveIntegerField(help_text="In minutes")
    servings = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    
    # Admin approval required for public visibility
    is_approved = models.BooleanField(default=False, help_text="Only approved recipes are visible to the public")

    def __str__(self):
        return self.title


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='recipes/')

    def __str__(self):
        return f"Image for {self.recipe.title}"
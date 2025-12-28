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
<<<<<<< HEAD
        return f"Image for {self.recipe.title}"
    
    # NEW: Comment on recipe
class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.recipe.title}"

    class Meta:
        ordering = ['-created_at']

# NEW: Rating on recipe (1-5 stars)
class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['author', 'recipe']

    def __str__(self):
        return f"{self.score} stars by {self.author.username} on {self.recipe.title}"

# NEW: Favorite recipe
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'recipe']

    def __str__(self):
        return f"{self.user.username} favorited {self.recipe.title}"
    


    
=======
        return f"Image for {self.recipe.title}"
>>>>>>> b86e3f5426852e49c5b397d2b5702cb7885b4b02

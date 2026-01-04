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
    is_approved = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # ADD THESE TWO FIELDS
    ingredients = models.TextField(blank=True, help_text="List of ingredients (one per line)")
    steps = models.TextField(blank=True, help_text="Preparation steps (one per line)")

    def __str__(self):
        return self.title

class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='recipes/')

    def __str__(self):

        return f"Image for {self.recipe.title}"
    
    # NEW: Comment on recipe
class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.recipe.title}"

    class Meta:
        ordering = ['-created_at']

# NEW: Rating on recipe (1-5 stars)

class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    score = models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('author', 'recipe')

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
    


    

        return f"Image for {self.recipe.title}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message}"

    class Meta:
        ordering = ['-created_at']




class RecipeAnalysis(models.Model):
    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE, related_name='analysis')
    nutritionist = models.ForeignKey(User, on_delete=models.CASCADE)
    calories = models.PositiveIntegerField(null=True, blank=True)
    proteins = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)  # 99999.9 max
    carbs = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    fats = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)

    # AJOUT DU HEALTH RATING (1 à 5 étoiles)
    HEALTH_RATING_CHOICES = [
        (1, '1 ⭐ Très mauvais'),
        (2, '2 ⭐⭐ Mauvais'),
        (3, '3 ⭐⭐⭐ Moyen'),
        (4, '4 ⭐⭐⭐⭐ Bon'),
        (5, '5 ⭐⭐⭐⭐⭐ Excellent'),
    ]
    health_rating = models.PositiveSmallIntegerField(
        choices=HEALTH_RATING_CHOICES,
        null=True,
        blank=True,
        help_text="Évaluation globale de la santé de la recette (1 à 5 étoiles)"
    )

    comment = models.TextField(blank=True, help_text="Commentaire du nutritionniste (facultatif)")
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analyse de '{self.recipe.title}' par Dr. {self.nutritionist.username}"

    class Meta:
        ordering = ['-analyzed_at']
        verbose_name = "Analyse Nutritionnelle"
        verbose_name_plural = "Analyses Nutritionnelles"



class NutritionFactSheet(models.Model):
    nutritionist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_sheets')
    title = models.CharField(max_length=200)
    description = models.TextField()
    # Champs nutritionnels détaillés (par 100g ou portion)
    energy_kcal = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    proteins = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    carbs = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    sugars = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    fats = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    saturated_fats = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    fiber = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    salt = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Nutrition Fact Sheet"
        verbose_name_plural = "Nutrition Fact Sheets"



class NutritionMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_nutrition_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_nutrition_messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    replied_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')


# Nouveaux champs pour suppression personnelle
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_recipient = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} → {self.recipient}: {self.subject}"

    class Meta:
        ordering = ['-sent_at']
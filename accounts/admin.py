# accounts/admin.py
from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile, Recipe, RecipeImage

# Custom action to approve chefs
def approve_chefs(modeladmin, request, queryset):
    for profile in queryset.filter(role='chef'):
        user = profile.user
        if not user.is_active:
            user.is_active = True
            user.save()

            # Send confirmation email (prints in console for dev)
            send_mail(
                'Your Chef Account on Dbara is Approved!',
                f'Hello {user.username},\n\nGreat news! Your chef account has been approved by the admin.\n\n'
                f'You can now log in at http://127.0.0.1:8000/login/ and start sharing your Tunisian recipes!\n\n'
                f'Thank you for joining Dbara!\n\nBest regards,\nThe Dbara Team',
                'noreply@dbara.com',
                [user.email],
                fail_silently=False,
            )
            modeladmin.message_user(request, f"Approved {user.username} and sent email.")
    modeladmin.message_user(request, "Selected chefs approved successfully!")

approve_chefs.short_description = "Approve selected chefs and send confirmation email"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'speciality', 'region', 'years_experience', 'user__is_active')
    list_filter = ('role', 'region', 'speciality')
    search_fields = ('user__username', 'user__email')
    actions = [approve_chefs]  # ← This makes the action appear


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_approved', 'views')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('title', 'author__username')
    actions = ['approve_recipes']

    def approve_recipes(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} recipe(s) approved.")
    approve_recipes.short_description = "Approve selected recipes"


@admin.register(RecipeImage)
class RecipeImageAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'image')
    search_fields = ('recipe__title',)
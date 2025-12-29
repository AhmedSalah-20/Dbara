# accounts/admin.py
from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile, Recipe, RecipeImage


# Custom action to approve Chefs and Nutritionists
def approve_professionals(modeladmin, request, queryset):
    approved_count = 0
    for profile in queryset.filter(role__in=['chef', 'nutritionist']):
        user = profile.user
        if not user.is_active:
            user.is_active = True
            user.save()

            role_name = "Chef" if profile.role == 'chef' else "Nutritionist"

            send_mail(
                f'Your {role_name} Account on Dbara is Approved!',
                f'Hello {user.username},\n\n'
                f'Great news! Your {role_name.lower()} account on Dbara has been approved.\n\n'
                f'You can now log in at http://127.0.0.1:8000/login/.\n\n'
                f'Thank you for joining our community!\n\n'
                f'Best regards,\nThe Dbara Team',
                settings.DEFAULT_FROM_EMAIL or 'noreply@dbara.com',
                [user.email],
                fail_silently=False,
            )
            modeladmin.message_user(request, f"Approved and emailed {user.username} ({role_name}).")
            approved_count += 1

    if approved_count == 0:
        modeladmin.message_user(request, "No pending professional accounts selected.", level='warning')
    else:
        modeladmin.message_user(request, f"{approved_count} professional account(s) approved and notified.")


approve_professionals.short_description = "Approve selected profiles and send confirmation email"


# Admin for UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_role', 'speciality', 'region', 'years_experience', 'user__is_active')
    list_filter = ('role', 'region', 'speciality')
    search_fields = ('user__username', 'user__email')
    actions = [approve_professionals]

    def get_role(self, obj):
        if obj.user.is_staff or obj.user.is_superuser:
            return "Administrator"
        return obj.role or "-"
    get_role.short_description = "Role"


# Admin for Recipe
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_approved', 'views')
    list_filter = ('is_approved', 'created_at', 'author')
    search_fields = ('title', 'author__username')
    actions = ['approve_recipes']  # ← Now attached

    def approve_recipes(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"{updated} recipe(s) approved successfully.")
    approve_recipes.short_description = "Approve selected recipes"


# Admin for RecipeImage
@admin.register(RecipeImage)
class RecipeImageAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'image')
    search_fields = ('recipe__title',)
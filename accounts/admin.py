from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile

# Inline admin pour afficher le profil utilisateur dans l'admin User
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ('phone_number', 'date_of_birth', 'avatar')

# Extension de l'admin User pour inclure le profil
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Re-registration de User avec notre admin personnalisé
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Enregistrement du UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'date_of_birth', 'created_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

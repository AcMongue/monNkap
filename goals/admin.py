from django.contrib import admin
from .models import Goal, Contribution


class ContributionInline(admin.TabularInline):
    """Inline admin pour afficher les contributions dans l'admin Goal."""
    model = Contribution
    extra = 1
    readonly_fields = ('created_at',)


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'target_amount', 'current_amount', 'get_progress', 'deadline', 'status')
    list_filter = ('status', 'deadline', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'get_progress_percentage')
    date_hierarchy = 'deadline'
    inlines = [ContributionInline]
    
    def get_progress(self, obj):
        """Affiche le pourcentage de progression."""
        return f"{obj.get_progress_percentage():.1f}%"
    get_progress.short_description = 'Progression'
    
    def get_queryset(self, request):
        """Optimise les requêtes."""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('goal', 'amount', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('goal__title', 'note')
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        """Optimise les requêtes."""
        qs = super().get_queryset(request)
        return qs.select_related('goal', 'goal__user')

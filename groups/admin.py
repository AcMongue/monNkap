from django.contrib import admin
from .models import Group, Membership, GroupContribution, GroupGoal


class MembershipInline(admin.TabularInline):
    """Inline admin pour afficher les membres dans l'admin Group."""
    model = Membership
    extra = 1
    readonly_fields = ('joined_at',)


class GroupContributionInline(admin.TabularInline):
    """Inline admin pour afficher les contributions dans l'admin Group."""
    model = GroupContribution
    extra = 1
    readonly_fields = ('created_at',)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'target_amount', 'current_amount', 'get_progress', 'deadline', 'status')
    list_filter = ('status', 'deadline', 'created_at')
    search_fields = ('name', 'description', 'creator__username')
    readonly_fields = ('created_at', 'updated_at', 'get_progress_percentage')
    date_hierarchy = 'deadline'
    inlines = [MembershipInline, GroupContributionInline]
    
    def get_progress(self, obj):
        """Affiche le pourcentage de progression."""
        return f"{obj.get_progress_percentage():.1f}%"
    get_progress.short_description = 'Progression'
    
    def get_queryset(self, request):
        """Optimise les requêtes."""
        qs = super().get_queryset(request)
        return qs.select_related('creator')


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('user__username', 'group__name')
    readonly_fields = ('joined_at',)
    
    def get_queryset(self, request):
        """Optimise les requêtes."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'group')


@admin.register(GroupContribution)
class GroupContributionAdmin(admin.ModelAdmin):
    list_display = ('group', 'goal', 'user', 'amount', 'date', 'created_at')
    list_filter = ('date', 'created_at', 'goal')
    search_fields = ('group__name', 'user__username', 'note', 'goal__title')
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'
    autocomplete_fields = ('goal',)
    
    def get_queryset(self, request):
        """Optimise les requêtes."""
        qs = super().get_queryset(request)
        return qs.select_related('group', 'user', 'goal')


@admin.register(GroupGoal)
class GroupGoalAdmin(admin.ModelAdmin):
    """Administration des objectifs de groupe."""
    list_display = ('title', 'group', 'goal_type', 'target_amount', 'current_amount', 'get_progress', 'deadline', 'status', 'created_by')
    list_filter = ('status', 'goal_type', 'deadline', 'created_at')
    search_fields = ('title', 'description', 'group__name', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at', 'get_progress_percentage', 'get_remaining_amount')
    date_hierarchy = 'deadline'
    fieldsets = (
        ('Informations générales', {
            'fields': ('group', 'title', 'description', 'goal_type', 'created_by')
        }),
        ('Objectif financier', {
            'fields': ('target_amount', 'current_amount', 'get_remaining_amount', 'get_progress_percentage')
        }),
        ('Échéance et statut', {
            'fields': ('deadline', 'status')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_progress(self, obj):
        """Affiche le pourcentage de progression."""
        return f"{obj.get_progress_percentage():.1f}%"
    get_progress.short_description = 'Progression'
    
    def get_queryset(self, request):
        """Optimise les requêtes."""
        qs = super().get_queryset(request)
        return qs.select_related('group', 'created_by')

from django.contrib import admin
from .models import Group, Membership, GroupContribution


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
    list_display = ('group', 'user', 'amount', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('group__name', 'user__username', 'note')
    readonly_fields = ('created_at',)
    date_hierarchy = 'date'
    
    def get_queryset(self, request):
        """Optimise les requêtes."""
        qs = super().get_queryset(request)
        return qs.select_related('group', 'user')

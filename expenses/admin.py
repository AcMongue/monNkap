from django.contrib import admin
from .models import Category, Expense, Budget


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'user', 'category', 'amount', 'date', 'created_at')
    list_filter = ('category', 'date', 'created_at')
    search_fields = ('description', 'notes', 'user__username')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    def get_queryset(self, request):
        """Optimise les requêtes en préchargeant les relations."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'category')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'month', 'year', 'get_status_display', 'created_at')
    list_filter = ('year', 'month', 'category', 'created_at')
    search_fields = ('user__username', 'category__name')
    readonly_fields = ('created_at', 'updated_at', 'get_spent_display', 'get_remaining_display', 'get_progress_display')
    
    fieldsets = (
        ('Budget', {
            'fields': ('user', 'category', 'amount', 'month', 'year', 'alert_threshold')
        }),
        ('Statistiques', {
            'fields': ('get_spent_display', 'get_remaining_display', 'get_progress_display'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status_display(self, obj):
        status = obj.get_status()
        colors = {'ok': 'green', 'warning': 'orange', 'exceeded': 'red'}
        labels = {'ok': 'OK', 'warning': 'Alerte', 'exceeded': 'Dépassé'}
        return f'<span style="color: {colors.get(status, "black")}; font-weight: bold;">{labels.get(status, status)}</span>'
    get_status_display.short_description = 'Statut'
    get_status_display.allow_tags = True
    
    def get_spent_display(self, obj):
        return f"{obj.get_spent_amount():.2f} FCFA"
    get_spent_display.short_description = 'Dépensé'
    
    def get_remaining_display(self, obj):
        return f"{obj.get_remaining_amount():.2f} FCFA"
    get_remaining_display.short_description = 'Restant'
    
    def get_progress_display(self, obj):
        return f"{obj.get_progress_percentage():.1f}%"
    get_progress_display.short_description = 'Progression'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user', 'category')

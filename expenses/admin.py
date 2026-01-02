from django.contrib import admin
from .models import Category, Expense


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

from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.expense_list_view, name='list'),
    path('add/', views.expense_create_view, name='create'),
    path('<int:pk>/edit/', views.expense_update_view, name='update'),
    path('<int:pk>/delete/', views.expense_delete_view, name='delete'),
    path('statistics/', views.expense_statistics_view, name='statistics'),
    path('categories/', views.category_list_view, name='categories'),
    path('export/csv/', views.export_expenses_csv, name='export_csv'),
    
    # Budgets
    path('budgets/', views.budget_list_view, name='budget_list'),
    path('budgets/add/', views.budget_create_view, name='budget_create'),
    path('budgets/<int:pk>/edit/', views.budget_update_view, name='budget_update'),
    path('budgets/<int:pk>/delete/', views.budget_delete_view, name='budget_delete'),
]

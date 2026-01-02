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
]

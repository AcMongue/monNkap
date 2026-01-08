from django.urls import path
from . import views
from .api import search_users_api

app_name = 'groups'

urlpatterns = [
    path('', views.group_list_view, name='list'),
    path('help/', views.group_help_view, name='help'),
    path('join/', views.join_group_view, name='join'),
    path('join/<str:invite_code>/', views.join_group_view, name='join_with_code'),
    path('create/', views.group_create_view, name='create'),
    path('<int:pk>/', views.group_detail_view, name='detail'),
    path('<int:pk>/edit/', views.group_update_view, name='update'),
    path('<int:pk>/delete/', views.group_delete_view, name='delete'),
    path('<int:pk>/invite/', views.group_invite_view, name='invite'),
    path('<int:group_pk>/add-member/', views.member_add_view, name='add_member'),
    path('<int:group_pk>/remove-member/<int:member_pk>/', views.member_remove_view, name='remove_member'),
    path('<int:group_pk>/contribute/', views.contribution_create_view, name='contribute'),
    
    # Dépenses de groupe
    path('<int:group_pk>/expenses/', views.group_expense_list_view, name='expense_list'),
    path('<int:group_pk>/expenses/add/', views.group_expense_create_view, name='expense_create'),
    path('expenses/<int:pk>/', views.group_expense_detail_view, name='expense_detail'),
    path('expenses/split/<int:split_pk>/mark-paid/', views.mark_split_paid_view, name='mark_split_paid'),
    
    # Épargne de groupe
    path('<int:group_pk>/savings/', views.group_savings_list_view, name='savings_list'),
    path('<int:group_pk>/savings/create/', views.group_savings_create_view, name='savings_create'),
    path('savings/<int:pk>/', views.group_savings_detail_view, name='savings_detail'),
    path('savings/<int:pk>/contribute/', views.group_savings_contribute_view, name='savings_contribute'),
    path('savings/<int:pk>/edit/', views.group_savings_edit_view, name='savings_edit'),
    path('savings/<int:pk>/delete/', views.group_savings_delete_view, name='savings_delete'),
]

# API endpoints (à ajouter dans le futur dans une app séparée)
api_urlpatterns = [
    path('api/search-users/', search_users_api, name='api_search_users'),
]

urlpatterns += api_urlpatterns

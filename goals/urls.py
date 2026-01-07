from django.urls import path
from . import views

app_name = 'goals'

urlpatterns = [
    path('', views.goal_list_view, name='list'),
    path('<int:pk>/', views.goal_detail_view, name='detail'),
    path('create/', views.goal_create_view, name='create'),
    path('<int:pk>/edit/', views.goal_update_view, name='update'),
    path('<int:pk>/delete/', views.goal_delete_view, name='delete'),
    path('<int:goal_pk>/contribute/', views.contribution_create_view, name='contribute'),
    path('<int:pk>/complete/', views.complete_goal_view, name='complete'),
    path('<int:pk>/release/', views.release_goal_funds_view, name='release'),
]

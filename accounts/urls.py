from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Portefeuille
    path('wallet/', views.wallet_dashboard_view, name='wallet'),
    path('wallet/add-transaction/', views.add_transaction_view, name='add_transaction'),
    path('wallet/allocate/<int:goal_pk>/', views.allocate_to_goal_view, name='allocate_to_goal'),
]

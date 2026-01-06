from django.urls import path
from . import views
from .password_reset_view import SafePasswordResetView
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Réinitialisation de mot de passe
    path('password_reset/', SafePasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Portefeuille
    path('wallet/', views.wallet_dashboard_view, name='wallet'),
    path('wallet/add-transaction/', views.add_transaction_view, name='add_transaction'),
    path('wallet/allocate/<int:goal_pk>/', views.allocate_to_goal_view, name='allocate_to_goal'),
]

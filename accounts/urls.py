from django.urls import path
from . import views
from .password_reset_view import SafePasswordResetView
from .admin_views import fix_wallet_expenses_view
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Réinitialisation de mot de passe avec templates personnalisés
    path('password_reset/', 
         SafePasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt'
         ), 
         name='password_reset'),
    
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/reset/done/'
         ), 
         name='password_reset_confirm'),
    
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Portefeuille
    path('wallet/', views.wallet_dashboard_view, name='wallet'),
    path('wallet/add-transaction/', views.add_transaction_view, name='add_transaction'),
    path('wallet/allocate/<int:goal_pk>/', views.allocate_to_goal_view, name='allocate_to_goal'),
    
    # Admin tools (staff only)
    path('admin/fix-wallet-expenses/', fix_wallet_expenses_view, name='fix_wallet_expenses'),
]

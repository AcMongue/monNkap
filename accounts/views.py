from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django_ratelimit.decorators import ratelimit
from decimal import Decimal
from .forms import UserRegistrationForm, UserUpdateForm, ProfileUpdateForm
from .wallet_forms import WalletTransactionForm, GoalAllocationForm
from .models import Wallet, WalletTransaction, GoalAllocation, EmailVerificationCode
from .emails import send_welcome_email, send_goal_achieved_email, send_low_balance_alert
from .verification_emails import send_verification_code_email
from goals.models import Goal
from .motivation_messages import get_wallet_income_message


@ratelimit(key='ip', rate='5/h', method='POST')
def register_view(request):
    """
    Vue d'inscription d'un nouvel utilisateur.
    Envoie un code de vérification par email.
    Rate limited: 5 tentatives par heure par IP.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    # Vérifier si rate limited
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, 'Trop de tentatives. Veuillez réessayer dans une heure.')
        return render(request, 'accounts/register.html', {'form': UserRegistrationForm()})
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Créer l'utilisateur mais ne pas le connecter
            user = form.save(commit=False)
            user.is_active = False  # Désactiver jusqu'à vérification
            user.save()
            
            # Créer le profil (via signal)
            form.save_m2m()
            
            # Générer et envoyer le code de vérification
            verification_code = EmailVerificationCode.create_for_user(user)
            
            try:
                send_verification_code_email(user, verification_code.code)
                messages.success(request, f'Compte créé! Vérifiez votre email pour le code de vérification.')
                # Stocker l'ID utilisateur en session pour la page de vérification
                request.session['pending_verification_user_id'] = user.id
                return redirect('accounts:verify_email')
            except Exception as e:
                print(f"Erreur envoi code de vérification: {e}")
                messages.error(request, "Erreur lors de l'envoi du code. Veuillez contacter le support.")
                user.delete()  # Supprimer l'utilisateur si l'email n'a pas pu être envoyé
                return render(request, 'accounts/register.html', {'form': form})
        else:
            messages.error(request, 'Erreur lors de la création du compte. Veuillez vérifier les informations.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@sensitive_post_parameters('password')
@never_cache
@ratelimit(key='ip', rate='5/5m', method='POST')
def login_view(request):
    """
    Vue de connexion des utilisateurs.
    Rate limited: 5 tentatives par 5 minutes par IP.
    Protection contre les attaques par force brute via django-axes.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    # Vérifier si rate limited
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, 'Trop de tentatives de connexion. Veuillez réessayer dans 5 minutes.')
        return render(request, 'accounts/login.html', {'form': AuthenticationForm()})
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue, {username}!')
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """
    Vue de déconnexion.
    """
    logout(request)
    messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """
    Vue du profil utilisateur avec possibilité de modification.
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Erreur lors de la mise à jour du profil.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'accounts/profile.html', context)


# ==================== VUES DU PORTEFEUILLE ====================

@login_required
def wallet_dashboard_view(request):
    """
    Tableau de bord du portefeuille avec vue d'ensemble des finances.
    """
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Récupérer les transactions récentes
    recent_transactions = WalletTransaction.objects.filter(wallet=wallet).select_related('category', 'expense').order_by('-date')[:10]
    
    # Récupérer les objectifs avec leurs allocations
    goals = Goal.objects.filter(user=request.user, status='active')
    goal_allocations = []
    for goal in goals:
        allocated = GoalAllocation.objects.filter(
            wallet=wallet,
            goal=goal
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        goal_allocations.append({
            'goal': goal,
            'allocated': allocated,
            'percentage': (allocated / goal.target_amount * 100) if goal.target_amount > 0 else 0
        })
    
    # Statistiques
    total_income = WalletTransaction.objects.filter(
        wallet=wallet,
        transaction_type='income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    total_expense = WalletTransaction.objects.filter(
        wallet=wallet,
        transaction_type='expense'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    context = {
        'wallet': wallet,
        'recent_transactions': recent_transactions,
        'goal_allocations': goal_allocations,
        'total_income': total_income,
        'total_expense': total_expense
    }
    
    return render(request, 'accounts/wallet_dashboard.html', context)


@login_required
def add_transaction_view(request):
    """
    Ajouter une transaction au portefeuille.
    """
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = WalletTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.wallet = wallet
            transaction.save()
            
            # Vérifier si le solde est bas après une sortie
            if transaction.transaction_type == 'expense' and wallet.available_balance < 50000:
                try:
                    send_low_balance_alert(request.user, wallet)
                except Exception as e:
                    print(f"Erreur envoi email alerte solde: {e}")
            
            type_label = "Entrée" if transaction.transaction_type == 'income' else "Sortie"
            messages.success(request, f'{type_label} de {transaction.amount} FCFA enregistrée!')
            
            # Message de motivation pour les entrées d'argent
            if transaction.transaction_type == 'income':
                motivation = get_wallet_income_message()
                messages.info(request, f"{motivation['icon']} {motivation['message']}")
            
            return redirect('accounts:wallet')
    else:
        form = WalletTransactionForm()
    
    # Récupérer les catégories existantes pour les suggestions
    from expenses.models import Category
    existing_categories = Category.objects.all().order_by('name')
    
    context = {
        'form': form,
        'wallet': wallet,
        'title': 'Ajouter une Transaction',
        'existing_categories': existing_categories
    }
    
    return render(request, 'accounts/transaction_form.html', context)


@login_required
def allocate_to_goal_view(request, goal_pk):
    """
    Allouer des fonds du portefeuille à un objectif.
    """
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    goal = get_object_or_404(Goal, pk=goal_pk, user=request.user)
    
    # Recalculer les soldes pour avoir les données à jour
    wallet.update_balances()
    
    if request.method == 'POST':
        form = GoalAllocationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            
            # Double vérification du solde disponible
            wallet.update_balances()  # Recalculer avant validation
            
            if amount > wallet.available_balance:
                messages.error(
                    request, 
                    f'❌ Solde disponible insuffisant. Disponible : {wallet.available_balance} FCFA, '
                    f'vous essayez d\'allouer : {amount} FCFA.'
                )
                return render(request, 'accounts/allocate_form.html', {
                    'form': form,
                    'wallet': wallet,
                    'goal': goal,
                    'title': f'Allouer des fonds à {goal.title}'
                })
            
            try:
                allocation = form.save(commit=False)
                allocation.wallet = wallet
                allocation.goal = goal
                allocation.save()  # Le modèle validera à nouveau dans clean()
                
                messages.success(request, f'✅ {amount} FCFA alloués avec succès à {goal.title}!')
                return redirect('accounts:wallet')
            except Exception as e:
                messages.error(request, f'❌ Erreur lors de l\'allocation : {str(e)}')
    else:
        form = GoalAllocationForm()
    
    context = {
        'form': form,
        'wallet': wallet,
        'goal': goal,
        'title': f'Allouer des fonds à {goal.title}'
    }
    
    return render(request, 'accounts/allocate_form.html', context)


@ratelimit(key='ip', rate='10/h', method='POST')
def verify_email_view(request):
    """
    Vue pour saisir le code de vérification d'email
    """
    # Récupérer l'utilisateur en attente de vérification
    user_id = request.session.get('pending_verification_user_id')
    if not user_id:
        messages.error(request, 'Session expirée. Veuillez vous inscrire à nouveau.')
        return redirect('accounts:register')
    
    try:
        user = User.objects.get(id=user_id, is_active=False)
    except User.DoesNotExist:
        messages.error(request, 'Utilisateur introuvable.')
        return redirect('accounts:register')
    
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, 'Trop de tentatives. Attendez un peu.')
        return render(request, 'accounts/verify_email.html', {'email': user.email})
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        
        if not code:
            messages.error(request, 'Veuillez entrer le code.')
            return render(request, 'accounts/verify_email.html', {'email': user.email})
        
        # Chercher le code valide le plus récent
        verification = user.verification_codes.filter(
            code=code,
            is_used=False
        ).first()
        
        if verification and verification.is_valid():
            # Activer l'utilisateur
            user.is_active = True
            user.save()
            
            # Marquer le code comme utilisé
            verification.mark_as_used()
            
            # Nettoyer la session
            del request.session['pending_verification_user_id']
            
            # Envoyer l'email de bienvenue
            try:
                send_welcome_email(user)
            except Exception as e:
                print(f"Erreur envoi email de bienvenue: {e}")
            
            # Connecter automatiquement l'utilisateur
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            messages.success(request, f'✅ Email vérifié! Bienvenue {user.username}!')
            return redirect('dashboard:home')
        else:
            messages.error(request, '❌ Code invalide ou expiré. Vérifiez votre email.')
            return render(request, 'accounts/verify_email.html', {'email': user.email})
    
    return render(request, 'accounts/verify_email.html', {'email': user.email})


@ratelimit(key='ip', rate='3/h', method='POST')
def resend_verification_code_view(request):
    """
    Renvoie un nouveau code de vérification
    """
    user_id = request.session.get('pending_verification_user_id')
    if not user_id:
        messages.error(request, 'Session expirée.')
        return redirect('accounts:register')
    
    try:
        user = User.objects.get(id=user_id, is_active=False)
    except User.DoesNotExist:
        messages.error(request, 'Utilisateur introuvable.')
        return redirect('accounts:register')
    
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        messages.error(request, 'Trop de tentatives. Attendez un peu.')
        return redirect('accounts:verify_email')
    
    # Générer un nouveau code
    verification_code = EmailVerificationCode.create_for_user(user)
    
    try:
        send_verification_code_email(user, verification_code.code)
        messages.success(request, '✉️ Un nouveau code a été envoyé à votre email.')
    except Exception as e:
        messages.error(request, "Erreur lors de l'envoi du code.")
    
    return redirect('accounts:verify_email')

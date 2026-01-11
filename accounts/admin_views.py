"""
Vues d'administration accessibles uniquement aux superusers.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction as db_transaction
from django.db.models.signals import post_save
from .models import WalletTransaction
from expenses.models import Expense


@staff_member_required
def fix_wallet_expenses_view(request):
    """
    Vue pour corriger les anciennes transactions du portefeuille.
    Accessible uniquement aux admins via /admin/fix-wallet-expenses/
    """
    if request.method == 'POST':
        # Exécuter la correction
        transactions_without_expense = WalletTransaction.objects.filter(
            transaction_type='expense',
            expense__isnull=True
        ).select_related('wallet__user', 'category')
        
        results = {
            'total': transactions_without_expense.count(),
            'created': 0,
            'errors': [],
            'details': []
        }
        
        # Désactiver temporairement le signal pour éviter les doublons
        from django.db.models import signals
        from .models import Wallet
        
        # Trouver le receiver du signal
        receivers_backup = signals.post_save._live_receivers(Expense)
        
        # Déconnecter tous les receivers de Expense
        for receiver in list(receivers_backup):
            signals.post_save.disconnect(receiver[1][0], sender=Expense)
        
        try:
            for trans in transactions_without_expense:
                try:
                    with db_transaction.atomic():
                        expense = Expense.objects.create(
                            user=trans.wallet.user,
                            amount=trans.amount,
                            category=trans.category,
                            description=trans.description,
                            date=trans.date
                        )
                        
                        trans.expense = expense
                        trans.save()
                        
                        results['created'] += 1
                        results['details'].append({
                            'transaction_id': trans.id,
                            'expense_id': expense.id,
                            'amount': str(trans.amount),
                            'description': trans.description,
                            'user': trans.wallet.user.username
                        })
                        
                except Exception as e:
                    results['errors'].append({
                        'transaction_id': trans.id,
                        'error': str(e)
                    })
        finally:
            # Reconnecter tous les receivers
            for receiver in receivers_backup:
                signals.post_save.connect(receiver[1][0], sender=Expense, weak=receiver[1][1])
        
        return JsonResponse(results)
    
    # GET - Afficher le formulaire
    transactions_without_expense = WalletTransaction.objects.filter(
        transaction_type='expense',
        expense__isnull=True
    ).select_related('wallet__user', 'category')
    
    context = {
        'count': transactions_without_expense.count(),
        'transactions': transactions_without_expense[:20]  # Preview des 20 premières
    }
    
    return render(request, 'accounts/admin_fix_wallet.html', context)

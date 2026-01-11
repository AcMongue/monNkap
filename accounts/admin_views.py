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
        # Importer le signal ici pour le désactiver temporairement
        from .wallet_models import create_or_update_wallet_transaction_from_expense
        
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
        
        for trans in transactions_without_expense:
            try:
                with db_transaction.atomic():
                    # Désactiver le signal temporairement pour éviter la création d'une 2e transaction
                    post_save.disconnect(create_or_update_wallet_transaction_from_expense, sender=Expense)
                    
                    try:
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
                    finally:
                        # Réactiver le signal
                        post_save.connect(create_or_update_wallet_transaction_from_expense, sender=Expense)
                    
            except Exception as e:
                results['errors'].append({
                    'transaction_id': trans.id,
                    'error': str(e)
                })
        
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

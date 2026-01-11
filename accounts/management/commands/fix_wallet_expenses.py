"""
Commande pour corriger les anciennes transactions du portefeuille
qui n'ont pas de dépenses associées.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import WalletTransaction, Wallet
from expenses.models import Expense


class Command(BaseCommand):
    help = 'Crée les dépenses manquantes pour les sorties du portefeuille'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher ce qui serait fait sans appliquer les changements',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Trouver toutes les transactions de type 'expense' sans dépense associée
        transactions_without_expense = WalletTransaction.objects.filter(
            transaction_type='expense',
            expense__isnull=True
        ).select_related('wallet__user', 'category')
        
        count = transactions_without_expense.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('✅ Aucune transaction à corriger!'))
            return
        
        self.stdout.write(f'🔍 Trouvé {count} transaction(s) à corriger...\n')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODE DRY-RUN - Aucune modification appliquée\n'))
        
        created_count = 0
        error_count = 0
        
        for trans in transactions_without_expense:
            try:
                if dry_run:
                    self.stdout.write(
                        f'  → Créerait dépense: {trans.amount} FCFA - {trans.description} '
                        f'(User: {trans.wallet.user.username}, Date: {trans.date})'
                    )
                else:
                    # Créer la dépense associée
                    with transaction.atomic():
                        expense = Expense.objects.create(
                            user=trans.wallet.user,
                            amount=trans.amount,
                            category=trans.category,
                            description=trans.description,
                            date=trans.date
                        )
                        
                        # Lier la transaction à la dépense
                        trans.expense = expense
                        trans.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  ✅ Créé dépense #{expense.id}: {trans.amount} FCFA - {trans.description}'
                            )
                        )
                        created_count += 1
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ❌ Erreur pour transaction #{trans.id}: {str(e)}'
                    )
                )
                error_count += 1
        
        # Résumé
        self.stdout.write('\n' + '='*60)
        if dry_run:
            self.stdout.write(self.style.WARNING(f'📊 {count} dépense(s) seraient créées'))
            self.stdout.write(self.style.WARNING('\nPour appliquer les changements, lancez:'))
            self.stdout.write(self.style.WARNING('python manage.py fix_wallet_expenses'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ {created_count} dépense(s) créée(s)'))
            if error_count > 0:
                self.stdout.write(self.style.ERROR(f'❌ {error_count} erreur(s)'))
            self.stdout.write(self.style.SUCCESS('\n🎉 Correction terminée!'))

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Wallet(models.Model):
    """
    Portefeuille personnel de l'utilisateur.
    Permet de gérer son argent et de le répartir entre différents objectifs.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wallet',
        verbose_name='Utilisateur'
    )
    total_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Solde total'
    )
    available_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Solde disponible'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière modification'
    )

    class Meta:
        verbose_name = 'Portefeuille'
        verbose_name_plural = 'Portefeuilles'

    def __str__(self):
        return f"Portefeuille de {self.user.username} - {self.total_balance} FCFA"

    def get_allocated_amount(self):
        """Montant total alloué aux objectifs."""
        return self.total_balance - self.available_balance

    def update_balances(self):
        """Recalcule les soldes en fonction des transactions et allocations."""
        from django.db.models import Sum
        
        # Total des entrées
        income = WalletTransaction.objects.filter(
            wallet=self,
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Total des sorties
        expense = WalletTransaction.objects.filter(
            wallet=self,
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Total alloué aux objectifs
        allocated = GoalAllocation.objects.filter(
            wallet=self
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        self.total_balance = income - expense
        self.available_balance = self.total_balance - allocated
        self.save()


class WalletTransaction(models.Model):
    """
    Transactions du portefeuille (entrées et sorties d'argent).
    """
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Entrée'),
        ('expense', 'Sortie'),
    ]
    
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Portefeuille'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        verbose_name='Type'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Montant'
    )
    category = models.ForeignKey(
        'expenses.Category',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='wallet_transactions',
        verbose_name='Catégorie'
    )
    expense = models.OneToOneField(
        'expenses.Expense',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='wallet_transaction',
        verbose_name='Dépense liée'
    )
    description = models.CharField(
        max_length=255,
        verbose_name='Description'
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name='Date'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-date', '-created_at']

    def __str__(self):
        type_label = "+" if self.transaction_type == 'income' else "-"
        return f"{type_label}{self.amount} FCFA - {self.description}"

    def save(self, *args, **kwargs):
        """Met à jour le portefeuille après une transaction."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.wallet.update_balances()


class GoalAllocation(models.Model):
    """
    Allocation de fonds du portefeuille vers un objectif d'épargne personnel.
    """
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='allocations',
        verbose_name='Portefeuille'
    )
    goal = models.ForeignKey(
        'goals.Goal',
        on_delete=models.CASCADE,
        related_name='allocations',
        verbose_name='Objectif'
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Montant alloué'
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name='Date d\'allocation'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )

    class Meta:
        verbose_name = 'Allocation'
        verbose_name_plural = 'Allocations'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.amount} FCFA alloués à {self.goal.title}"

# Signaux pour synchroniser Expense et WalletTransaction
@receiver(post_save, sender='expenses.Expense')
def create_or_update_wallet_transaction_from_expense(sender, instance, created, **kwargs):
    """
    Crée ou met à jour automatiquement une WalletTransaction quand une Expense est créée/modifiée.
    """
    if created:
        # Récupérer ou créer le wallet de l'utilisateur
        wallet, _ = Wallet.objects.get_or_create(user=instance.user)
        
        # Créer la transaction wallet
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='expense',
            amount=instance.amount,
            category=instance.category,
            expense=instance,
            description=instance.description,
            date=instance.date
        )
    else:
        # Mettre à jour la transaction existante
        if hasattr(instance, 'wallet_transaction') and instance.wallet_transaction:
            transaction = instance.wallet_transaction
            transaction.amount = instance.amount
            transaction.category = instance.category
            transaction.description = instance.description
            transaction.date = instance.date
            transaction.save()


@receiver(post_delete, sender='expenses.Expense')
def delete_wallet_transaction_from_expense(sender, instance, **kwargs):
    """
    Supprime la WalletTransaction associée quand une Expense est supprimée.
    """
    if hasattr(instance, 'wallet_transaction') and instance.wallet_transaction:
        instance.wallet_transaction.delete()
    def save(self, *args, **kwargs):
        """Met à jour le portefeuille après une allocation."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.wallet.update_balances()

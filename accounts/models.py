from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
import random
import string

class UserProfile(models.Model):
    """
    Extension du modèle User de Django pour ajouter des informations supplémentaires.
    Un profil est automatiquement créé lors de la création d'un utilisateur.
    """
    THEME_CHOICES = [
        ('auto', 'Automatique (système)'),
        ('light', 'Clair'),
        ('dark', 'Sombre'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Utilisateur'
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Numéro de téléphone'
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='Date de naissance'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Photo de profil'
    )
    theme_preference = models.CharField(
        max_length=10,
        choices=THEME_CHOICES,
        default='auto',
        verbose_name='Thème préféré'
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
        verbose_name = 'Profil utilisateur'
        verbose_name_plural = 'Profils utilisateurs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Profil de {self.user.username}"

    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur ou son username."""
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username


# Signal pour créer automatiquement un profil lors de la création d'un utilisateur
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crée un profil utilisateur automatiquement lors de la création d'un User."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde le profil utilisateur lors de la sauvegarde du User."""
    instance.profile.save()


# ==================== MODÈLES DE PORTEFEUILLE ====================

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

    def clean(self):
        """
        Validation métier : vérifier que le solde disponible est suffisant.
        """
        from django.core.exceptions import ValidationError
        
        if self.wallet and self.amount:
            # Recalculer le solde disponible en temps réel
            self.wallet.update_balances()
            
            # Si c'est une modification, ignorer l'ancien montant
            old_amount = Decimal('0.00')
            if self.pk:
                try:
                    old_allocation = GoalAllocation.objects.get(pk=self.pk)
                    old_amount = old_allocation.amount
                except GoalAllocation.DoesNotExist:
                    pass
            
            # Montant supplémentaire à allouer
            additional_amount = self.amount - old_amount
            
            # Vérifier si le solde disponible est suffisant
            if additional_amount > self.wallet.available_balance:
                raise ValidationError({
                    'amount': f'Solde disponible insuffisant. Disponible : {self.wallet.available_balance} FCFA, '
                              f'vous essayez d\'allouer : {additional_amount} FCFA supplémentaires.'
                })

    def save(self, *args, **kwargs):
        """Met à jour le portefeuille après une allocation."""
        # Valider avant de sauvegarder
        self.full_clean()
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.wallet.update_balances()


# Signal pour créer automatiquement un portefeuille
@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    """Crée un portefeuille automatiquement lors de la création d'un User."""
    if created:
        Wallet.objects.create(user=instance)


# ==================== SIGNAUX POUR LA SYNCHRONISATION EXPENSE <-> WALLET ====================

@receiver(post_save, sender='expenses.Expense')
def create_or_update_wallet_transaction_from_expense(sender, instance, created, **kwargs):
    """
    Crée ou met à jour une transaction de portefeuille quand une dépense est créée/modifiée.
    """
    # Récupérer le portefeuille de l'utilisateur
    wallet, _ = Wallet.objects.get_or_create(user=instance.user)
    
    # Vérifier si une transaction existe déjà pour cette dépense
    if hasattr(instance, 'wallet_transaction'):
        # Mise à jour
        transaction = instance.wallet_transaction
        transaction.amount = instance.amount
        transaction.category = instance.category
        transaction.description = instance.description
        transaction.date = instance.date
        transaction.save()
    else:
        # Création
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='expense',
            amount=instance.amount,
            category=instance.category,
            expense=instance,
            description=instance.description,
            date=instance.date
        )


@receiver(post_delete, sender='expenses.Expense')
def delete_wallet_transaction_from_expense(sender, instance, **kwargs):
    """
    Supprime la transaction de portefeuille quand une dépense est supprimée.
    """
    if hasattr(instance, 'wallet_transaction'):
        instance.wallet_transaction.delete()


class EmailVerificationCode(models.Model):
    """
    Code de vérification d'email à 6 chiffres
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Code {self.code} pour {self.user.username}"
    
    @classmethod
    def generate_code(cls):
        """Génère un code à 6 chiffres"""
        return ''.join(random.choices(string.digits, k=6))
    
    @classmethod
    def create_for_user(cls, user):
        """Crée un nouveau code pour un utilisateur"""
        code = cls.generate_code()
        expires_at = timezone.now() + timezone.timedelta(minutes=15)  # Valide 15 minutes
        
        return cls.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
    
    def is_valid(self):
        """Vérifie si le code est encore valide"""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Marque le code comme utilisé"""
        self.is_used = True
        self.save()

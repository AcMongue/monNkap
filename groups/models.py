from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
import secrets
import string


def generate_invite_code():
    """Génère un code d'invitation unique de 8 caractères."""
    characters = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(characters) for _ in range(8))


class Group(models.Model):
    """
    Groupes pour les objectifs financiers collaboratifs.
    Permet à plusieurs utilisateurs de cotiser pour un projet commun.
    """
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('completed', 'Complété'),
        ('cancelled', 'Annulé'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nom du groupe'
    )
    description = models.TextField(
        verbose_name='Description'
    )
    invite_code = models.CharField(
        max_length=8,
        unique=True,
        default=generate_invite_code,
        verbose_name='Code d\'invitation'
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_groups',
        verbose_name='Créateur'
    )
    members = models.ManyToManyField(
        User,
        through='Membership',
        related_name='member_groups',
        verbose_name='Membres'
    )
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Montant cible'
    )
    current_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Montant collecté'
    )
    deadline = models.DateField(
        verbose_name='Date limite'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Statut'
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
        verbose_name = 'Groupe'
        verbose_name_plural = 'Groupes'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_progress_percentage(self):
        """Calcule le pourcentage de progression du groupe."""
        if self.target_amount > 0:
            percentage = (self.current_amount / self.target_amount) * 100
            return min(percentage, 100)
        return 0

    def get_remaining_amount(self):
        """Calcule le montant restant pour atteindre l'objectif."""
        remaining = self.target_amount - self.current_amount
        return max(remaining, Decimal('0.00'))

    def is_overdue(self):
        """Vérifie si la date limite est dépassée."""
        return timezone.now().date() > self.deadline and self.status == 'active'

    def is_completed(self):
        """Vérifie si l'objectif du groupe est atteint."""
        return self.current_amount >= self.target_amount


class Membership(models.Model):
    """
    Relation entre un utilisateur et un groupe avec rôle.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('member', 'Membre'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Utilisateur'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        verbose_name='Groupe'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name='Rôle'
    )
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'adhésion'
    )

    class Meta:
        verbose_name = 'Adhésion'
        verbose_name_plural = 'Adhésions'
        unique_together = ('user', 'group')
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"


class GroupContribution(models.Model):
    """
    Contributions des membres vers un objectif de groupe.
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('paid', 'Payé'),
        ('cancelled', 'Annulé'),
    ]
    
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='contributions',
        verbose_name='Groupe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_contributions',
        verbose_name='Contributeur'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Montant'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='paid',
        verbose_name='Statut de paiement'
    )
    note = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Note'
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name='Date de la contribution'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )

    class Meta:
        verbose_name = 'Contribution de groupe'
        verbose_name_plural = 'Contributions de groupe'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount} FCFA pour {self.group.name}"

    def save(self, *args, **kwargs):
        """
        Met à jour le montant collecté du groupe lors de l'ajout d'une contribution.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Ne mettre à jour que si c'est une nouvelle contribution payée
        if is_new and self.payment_status == 'paid':
            self.group.current_amount += self.amount
            if self.group.current_amount >= self.group.target_amount:
                self.group.status = 'completed'
            self.group.save()


class GroupExpense(models.Model):
    """
    Dépenses partagées au sein d'un groupe.
    Permet aux membres de gérer leurs dépenses communes (couple, tontine, etc.)
    """
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='expenses',
        verbose_name='Groupe'
    )
    category = models.ForeignKey(
        'expenses.Category',
        on_delete=models.PROTECT,
        related_name='group_expenses',
        verbose_name='Catégorie'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Montant'
    )
    description = models.CharField(
        max_length=255,
        verbose_name='Description'
    )
    paid_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_expenses_paid',
        verbose_name='Payé par'
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name='Date'
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
        verbose_name = 'Dépense de groupe'
        verbose_name_plural = 'Dépenses de groupe'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description} - {self.amount} FCFA ({self.group.name})"
    
    def get_split_per_member(self):
        """Calcule la part de chaque membre."""
        member_count = self.group.members.count()
        if member_count > 0:
            return self.amount / member_count
        return Decimal('0.00')
    
    def get_unpaid_amount(self):
        """Calcule le montant non remboursé."""
        paid_splits = self.splits.filter(is_paid=True).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        return self.amount - paid_splits


class GroupExpenseSplit(models.Model):
    """
    Répartition d'une dépense de groupe entre les membres.
    Permet de suivre qui doit combien et qui a payé.
    """
    expense = models.ForeignKey(
        GroupExpense,
        on_delete=models.CASCADE,
        related_name='splits',
        verbose_name='Dépense'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expense_splits',
        verbose_name='Utilisateur'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Montant à payer'
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name='Payé'
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de paiement'
    )

    class Meta:
        verbose_name = 'Partage de dépense'
        verbose_name_plural = 'Partages de dépenses'
        unique_together = ('expense', 'user')

    def __str__(self):
        status = "✓" if self.is_paid else "✗"
        return f"{status} {self.user.username} - {self.amount} FCFA"


class GroupSavingsGoal(models.Model):
    """
    Objectifs d'épargne collaborative pour un groupe.
    Permet aux couples, tontines, amis de créer des objectifs d'épargne communs.
    Ex: Épargner pour un voyage, un projet, un investissement, etc.
    """
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('completed', 'Complété'),
        ('cancelled', 'Annulé'),
    ]
    
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='savings_goals',
        verbose_name='Groupe'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Titre de l\'objectif'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    target_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Montant cible'
    )
    current_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Montant épargné'
    )
    deadline = models.DateField(
        verbose_name='Date limite'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Statut'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_savings_goals',
        verbose_name='Créé par'
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
        verbose_name = 'Objectif d\'épargne de groupe'
        verbose_name_plural = 'Objectifs d\'épargne de groupe'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.group.name}"

    def get_progress_percentage(self):
        """Calcule le pourcentage de progression."""
        if self.target_amount > 0:
            percentage = (self.current_amount / self.target_amount) * 100
            return min(percentage, 100)
        return 0

    def get_remaining_amount(self):
        """Calcule le montant restant pour atteindre l'objectif."""
        remaining = self.target_amount - self.current_amount
        return max(remaining, Decimal('0.00'))

    def is_overdue(self):
        """Vérifie si la date limite est dépassée."""
        return timezone.now().date() > self.deadline and self.status == 'active'

    def is_completed(self):
        """Vérifie si l'objectif est atteint."""
        return self.current_amount >= self.target_amount

    def add_contribution(self, amount):
        """
        Ajoute une contribution à l'objectif d'épargne.
        Met à jour automatiquement le statut si l'objectif est atteint.
        """
        self.current_amount += amount
        if self.current_amount >= self.target_amount:
            self.status = 'completed'
        self.save()


class GroupSavingsContribution(models.Model):
    """
    Contributions individuelles vers un objectif d'épargne de groupe.
    Permet de suivre qui a contribué combien et quand.
    """
    savings_goal = models.ForeignKey(
        GroupSavingsGoal,
        on_delete=models.CASCADE,
        related_name='contributions',
        verbose_name='Objectif d\'épargne'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_savings_contributions',
        verbose_name='Contributeur'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Montant'
    )
    note = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Note'
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name='Date de la contribution'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )

    class Meta:
        verbose_name = 'Contribution d\'épargne de groupe'
        verbose_name_plural = 'Contributions d\'épargne de groupe'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.amount} FCFA vers {self.savings_goal.title}"

    def save(self, *args, **kwargs):
        """
        Met à jour automatiquement le montant épargné de l'objectif
        lors de l'ajout d'une contribution.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.savings_goal.add_contribution(self.amount)

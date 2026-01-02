from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal


class Goal(models.Model):
    """
    Objectifs financiers personnels des utilisateurs.
    Permet de définir un montant cible et suivre la progression.
    """
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('completed', 'Complété'),
        ('cancelled', 'Annulé'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='goals',
        verbose_name='Utilisateur'
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
        verbose_name='Montant actuel'
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
        verbose_name = 'Objectif financier'
        verbose_name_plural = 'Objectifs financiers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def get_progress_percentage(self):
        """Calcule le pourcentage de progression de l'objectif."""
        if self.target_amount > 0:
            percentage = (self.current_amount / self.target_amount) * 100
            return min(percentage, 100)  # Cap à 100%
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
        Ajoute une contribution à l'objectif.
        Met à jour automatiquement le statut si l'objectif est atteint.
        """
        self.current_amount += amount
        if self.current_amount >= self.target_amount:
            self.status = 'completed'
        self.save()


class Contribution(models.Model):
    """
    Contributions individuelles vers un objectif financier personnel.
    Permet de suivre l'historique des ajouts.
    """
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name='contributions',
        verbose_name='Objectif'
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
        verbose_name = 'Contribution'
        verbose_name_plural = 'Contributions'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.amount} FCFA vers {self.goal.title}"

    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour mettre à jour automatiquement
        le montant actuel de l'objectif lors de l'ajout d'une contribution.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.goal.add_contribution(self.amount)

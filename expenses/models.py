from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    """
    Catégories de dépenses (Alimentation, Transport, Loisirs, etc.)
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nom de la catégorie'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Description'
    )
    icon = models.CharField(
        max_length=50,
        default='bi-tag',
        verbose_name='Icône Bootstrap',
        help_text='Classe d\'icône Bootstrap (ex: bi-cart, bi-bus-front)'
    )
    color = models.CharField(
        max_length=7,
        default='#6c757d',
        verbose_name='Couleur',
        help_text='Code couleur hexadécimal (ex: #FF5733)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Expense(models.Model):
    """
    Dépenses individuelles des utilisateurs.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='expenses',
        verbose_name='Utilisateur'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='expenses',
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
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes supplémentaires'
    )
    date = models.DateField(
        verbose_name='Date de la dépense'
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
        verbose_name = 'Dépense'
        verbose_name_plural = 'Dépenses'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description} - {self.amount} FCFA ({self.date})"

    def get_category_name(self):
        """Retourne le nom de la catégorie ou 'Non catégorisé'."""
        return self.category.name if self.category else 'Non catégorisé'

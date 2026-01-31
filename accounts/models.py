from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
import random
import string
from .validators import validate_image_file

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
        verbose_name='Photo de profil',
        validators=[validate_image_file],
        help_text='Formats acceptés: JPG, PNG, GIF, WebP. Taille max: 5 MB.'
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


# ==================== IMPORT DES MODÈLES WALLET ====================
# Les modèles de portefeuille sont définis dans wallet_models.py
from .wallet_models import Wallet, WalletTransaction, GoalAllocation


# ==================== AUTRES MODÈLES ====================

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

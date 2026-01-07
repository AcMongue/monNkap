"""
Modèle pour la vérification d'email par code
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string

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

"""
Vue personnalisée pour la réinitialisation de mot de passe avec gestion d'erreur SMTP
"""
from django.contrib.auth.views import PasswordResetView
from django.contrib import messages
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)


class SafePasswordResetView(PasswordResetView):
    """
    Vue de réinitialisation de mot de passe avec gestion d'erreur SMTP robuste.
    Si l'envoi d'email échoue, affiche un message d'erreur explicite au lieu de crash.
    """
    
    def form_valid(self, form):
        """
        Si l'envoi d'email échoue (timeout SMTP, erreur de connexion, etc.),
        capture l'erreur et affiche un message informatif à l'utilisateur.
        """
        try:
            # Tenter d'envoyer l'email normalement
            return super().form_valid(form)
        except Exception as e:
            # Logger l'erreur pour le débogage
            logger.error(f"Erreur lors de l'envoi de l'email de réinitialisation: {e}")
            
            # Message utilisateur explicite
            messages.error(
                self.request, 
                "⚠️ Erreur lors de l'envoi de l'email de réinitialisation. "
                "Le service d'envoi d'emails est temporairement indisponible. "
                "Veuillez réessayer dans quelques minutes ou contacter l'administrateur."
            )
            
            # Rediriger vers la page de reset plutôt que de crasher
            return redirect('password_reset')

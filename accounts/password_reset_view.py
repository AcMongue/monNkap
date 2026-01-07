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
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = '/accounts/password_reset/done/'
    
    def save_form(self, form):
        """
        Override pour s'assurer que le domaine est correct dans l'email
        """
        opts = {
            'use_https': self.request.is_secure(),
            'from_email': None,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': None,
            'extra_email_context': None,
        }
        form.save(**opts)
    
    def form_valid(self, form):
        """
        Si l'envoi d'email échoue (timeout SMTP, erreur de connexion, etc.),
        capture l'erreur et affiche un message informatif à l'utilisateur.
        """
        try:
            # Logger la configuration email pour debug
            from django.conf import settings
            logger.info(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
            logger.info(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Non défini')}")
            logger.info(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Non défini')}")
            
            # Tenter d'envoyer l'email normalement
            self.save_form(form)
            logger.info("Email de réinitialisation envoyé avec succès")
            return redirect(self.success_url)
            
        except Exception as e:
            # Logger l'erreur complète pour le débogage
            logger.error(f"Erreur lors de l'envoi de l'email de réinitialisation: {e}", exc_info=True)
            
            # Message utilisateur explicite
            messages.error(
                self.request, 
                "⚠️ Impossible d'envoyer l'email de réinitialisation. "
                "Veuillez vérifier votre adresse email ou contacter le support."
            )
            
            # Rediriger vers la page de reset plutôt que de crasher
            return redirect('accounts:password_reset')

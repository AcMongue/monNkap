from django.contrib.auth.views import PasswordResetView
from django.contrib import messages
from django.shortcuts import redirect
import logging

logger = logging.getLogger(__name__)


class SafePasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = '/accounts/password_reset/done/'
    
    def get_users(self, email):
        users = super().get_users(email)
        users_list = list(users)
        logger.info(f"Password reset requested for {email}")
        return iter(users_list)
    
    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            messages.error(
                self.request, 
                "⚠️ Impossible d'envoyer l'email de réinitialisation. "
                "Veuillez vérifier votre adresse email ou contacter le support."
            )
            return redirect('accounts:password_reset')

"""
Backend email personnalisé utilisant Resend API (contourne le blocage SMTP de Render)
"""
import os
import logging
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """
    Backend email utilisant l'API Resend au lieu de SMTP.
    Fonctionne sur Render où SMTP est bloqué.
    """
    
    def send_messages(self, email_messages):
        """
        Envoie les emails via l'API Resend
        """
        if not email_messages:
            return 0
        
        try:
            import resend
        except ImportError:
            logger.error("Le package 'resend' n'est pas installé. Installez-le avec: pip install resend")
            return 0
        
        # Configuration de l'API key
        api_key = os.environ.get('RESEND_API_KEY')
        if not api_key:
            logger.error("RESEND_API_KEY n'est pas définie dans les variables d'environnement")
            return 0
        
        resend.api_key = api_key
        sent_count = 0
        
        for message in email_messages:
            try:
                # Préparer les données
                params = {
                    "from": message.from_email,
                    "to": message.to,
                    "subject": message.subject,
                }
                
                # Ajouter le contenu
                if isinstance(message, EmailMultiAlternatives) and message.alternatives:
                    # Email HTML
                    for content, mimetype in message.alternatives:
                        if mimetype == 'text/html':
                            params["html"] = content
                            break
                    # Fallback texte
                    if message.body:
                        params["text"] = message.body
                else:
                    # Email texte simple
                    params["text"] = message.body
                
                # Envoyer via Resend
                response = resend.Emails.send(params)
                logger.info(f"Email envoyé via Resend: {response}")
                sent_count += 1
                
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi via Resend: {e}", exc_info=True)
                if self.fail_silently:
                    continue
                raise
        
        return sent_count

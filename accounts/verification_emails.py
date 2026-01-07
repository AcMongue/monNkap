"""
Email de vérification avec code
"""
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_verification_code_email(user, code):
    """
    Envoie un email avec le code de vérification à 6 chiffres
    """
    subject = "Votre code de vérification - MonNkap"
    
    message = f"""Bonjour {user.username},

Bienvenue sur MonNkap ! 🎉

Votre code de vérification est :

{code}

Ce code est valide pendant 15 minutes.

Si vous n'avez pas créé de compte sur MonNkap, ignorez cet email.

Cordialement,
L'équipe MonNkap

---
Votre assistant personnel de gestion financière"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Code de vérification envoyé à {user.email}")
        return True
    except Exception as e:
        logger.error(f"Erreur envoi code de vérification: {e}")
        return False

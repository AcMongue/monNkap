from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from decimal import Decimal


def send_welcome_email(user):
    """Envoie un email de bienvenue après inscription"""
    subject = 'Bienvenue sur MonNkap !'
    message = render_to_string('emails/welcome_email.html', {
        'user': user,
    })
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message,
        fail_silently=True,
    )


def send_goal_achieved_email(user, goal):
    """Envoie un email quand un objectif est atteint"""
    subject = f'🎉 Objectif atteint : {goal.title}'
    message = render_to_string('emails/goal_achieved.html', {
        'user': user,
        'goal': goal,
    })
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message,
        fail_silently=True,
    )


def send_monthly_report_email(user, stats):
    """Envoie un rapport mensuel des finances"""
    subject = f'📊 Votre rapport financier - {stats["month"]}'
    message = render_to_string('emails/monthly_report.html', {
        'user': user,
        'stats': stats,
    })
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message,
        fail_silently=True,
    )


def send_group_invitation_email(invited_by, recipient_email, group, invite_code):
    """Envoie une invitation à rejoindre un groupe"""
    subject = f'{invited_by.username} vous invite à rejoindre {group.name} sur FinTrack'
    message = render_to_string('emails/group_invitation.html', {
        'invited_by': invited_by,
        'recipient_email': recipient_email,
        'group': group,
        'invite_code': invite_code,
        'invite_url': f'{settings.SITE_URL}/groups/join/{invite_code}/',
    })
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [recipient_email],
        html_message=message,
        fail_silently=True,
    )


def send_low_balance_alert(user, wallet):
    """Alerte quand le solde disponible est bas"""
    subject = '⚠️ Alerte : Solde disponible faible'
    message = render_to_string('emails/low_balance_alert.html', {
        'user': user,
        'wallet': wallet,
    })
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message,
        fail_silently=True,
    )


def send_weekly_summary_email(user, summary_data):
    """Envoie un résumé hebdomadaire des activités"""
    subject = '📈 Votre résumé hebdomadaire FinTrack'
    message = render_to_string('emails/weekly_summary.html', {
        'user': user,
        'data': summary_data,
    })
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=message,
        fail_silently=True,
    )

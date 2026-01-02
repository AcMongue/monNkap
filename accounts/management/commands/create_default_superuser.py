import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Crée un superuser par défaut si aucun superuser n\'existe'

    def handle(self, *args, **options):
        # Vérifier si un superuser existe déjà
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING('Un superuser existe déjà'))
            return

        # Récupérer les informations depuis les variables d'environnement
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@monnkap.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'changeme123')

        # Créer le superuser
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Superuser "{username}" créé avec succès!')
        )

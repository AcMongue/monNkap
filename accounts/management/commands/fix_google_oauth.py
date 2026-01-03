from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os


class Command(BaseCommand):
    help = 'Nettoie et reconfigure complètement Google OAuth'

    def handle(self, *args, **options):
        # 1. Supprimer TOUTES les applications Google
        self.stdout.write("Suppression de toutes les applications Google...")
        deleted = SocialApp.objects.filter(provider='google').delete()
        self.stdout.write(self.style.SUCCESS(f"✓ {deleted[0]} applications supprimées"))
        
        # 2. Obtenir le site principal
        site = Site.objects.get(id=1)
        self.stdout.write(f"Site actuel: {site.domain}")
        
        # 3. Créer une nouvelle application Google
        self.stdout.write("\nCréation d'une nouvelle application Google...")
        
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            self.stdout.write(self.style.ERROR("✗ ERREUR: Variables GOOGLE_CLIENT_ID et GOOGLE_CLIENT_SECRET non définies"))
            return
        
        app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=client_secret,
        )
        app.sites.add(site)
        
        self.stdout.write(self.style.SUCCESS(f"✓ Application Google créée (ID: {app.id})"))
        self.stdout.write(f"  Provider: {app.provider}")
        self.stdout.write(f"  Client ID: {app.client_id[:20]}...")
        self.stdout.write(f"  Sites: {[s.domain for s in app.sites.all()]}")
        
        # 4. Vérification finale
        google_apps = SocialApp.objects.filter(provider='google')
        self.stdout.write(f"\n=== VÉRIFICATION FINALE ===")
        self.stdout.write(f"Applications Google: {google_apps.count()}")
        
        if google_apps.count() == 1:
            self.stdout.write(self.style.SUCCESS("✓ Configuration correcte!"))
        else:
            self.stdout.write(self.style.ERROR(f"✗ ERREUR: {google_apps.count()} applications trouvées"))

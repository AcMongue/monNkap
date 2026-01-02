from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Vérifie et affiche toutes les applications sociales et sites'

    def handle(self, *args, **options):
        # Vider le cache (ignorer si erreur)
        try:
            self.stdout.write("Vidage du cache...")
            cache.clear()
            self.stdout.write(self.style.SUCCESS("✓ Cache vidé!"))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"⚠️ Cache non disponible: {e}"))
        
        self.stdout.write("\n=== SITES ===")
        sites = Site.objects.all()
        for site in sites:
            self.stdout.write(f"ID: {site.id}, Domain: {site.domain}, Name: {site.name}")
        
        self.stdout.write("\n=== SOCIAL APPS ===")
        apps = SocialApp.objects.all()
        for app in apps:
            self.stdout.write(f"ID: {app.id}, Provider: {app.provider}, Name: {app.name}")
            self.stdout.write(f"  Sites: {[s.domain for s in app.sites.all()]}")
        
        self.stdout.write(f"\n=== TOTAL ===")
        self.stdout.write(f"Sites: {sites.count()}")
        self.stdout.write(f"Social Apps: {apps.count()}")
        
        # Nettoyer les doublons s'il y en a
        google_apps = SocialApp.objects.filter(provider='google')
        if google_apps.count() > 1:
            self.stdout.write(self.style.WARNING(f"\n⚠️ ATTENTION: {google_apps.count()} applications Google trouvées!"))
            self.stdout.write("Suppression des doublons...")
            # Garder seulement la première
            for app in google_apps[1:]:
                self.stdout.write(f"Suppression de l'app ID {app.id}")
                app.delete()
            self.stdout.write(self.style.SUCCESS("✓ Doublons supprimés!"))
        else:
            self.stdout.write(self.style.SUCCESS(f"\n✓ Configuration correcte: {google_apps.count()} application Google"))

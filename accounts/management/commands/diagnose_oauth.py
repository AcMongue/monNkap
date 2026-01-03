from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Diagnostique détaillé du problème MultipleObjectsReturned'

    def handle(self, *args, **options):
        site_id = getattr(settings, 'SITE_ID', 1)
        self.stdout.write(f"SITE_ID configuré: {site_id}")
        
        # Obtenir le site
        site = Site.objects.get(id=site_id)
        self.stdout.write(f"Site actuel: {site.domain}")
        
        # Méthode 1 : Toutes les apps Google
        self.stdout.write("\n=== Méthode 1: filter(provider='google') ===")
        apps1 = SocialApp.objects.filter(provider='google')
        self.stdout.write(f"Nombre d'apps: {apps1.count()}")
        for app in apps1:
            self.stdout.write(f"  - ID: {app.id}, Name: {app.name}, Sites: {[s.id for s in app.sites.all()]}")
        
        # Méthode 2 : Apps Google pour le site actuel
        self.stdout.write("\n=== Méthode 2: filter(provider='google', sites__id=site_id) ===")
        apps2 = SocialApp.objects.filter(provider='google', sites__id=site_id)
        self.stdout.write(f"Nombre d'apps: {apps2.count()}")
        for app in apps2:
            self.stdout.write(f"  - ID: {app.id}, Name: {app.name}")
        
        # Méthode 3 : Ce que fait allauth (simulation)
        self.stdout.write("\n=== Méthode 3: Simulation allauth get_app ===")
        try:
            # Requête similaire à ce que fait allauth
            apps3 = SocialApp.objects.filter(
                provider='google',
                sites__id=site_id
            )
            count = apps3.count()
            self.stdout.write(f"Nombre d'apps trouvées: {count}")
            
            if count == 0:
                self.stdout.write(self.style.ERROR("✗ Aucune application trouvée"))
            elif count == 1:
                app = apps3.get()
                self.stdout.write(self.style.SUCCESS(f"✓ Une seule app trouvée (ID: {app.id})"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ PROBLÈME: {count} applications trouvées"))
                for app in apps3:
                    self.stdout.write(f"  - ID: {app.id}, Name: {app.name}, Provider: {app.provider}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ ERREUR: {type(e).__name__}: {e}"))
        
        # Vérification de doublons dans la table de liaison
        self.stdout.write("\n=== Vérification table de liaison ===")
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT socialapp_id, site_id, COUNT(*)
                FROM socialaccount_socialapp_sites
                GROUP BY socialapp_id, site_id
                HAVING COUNT(*) > 1
            """)
            duplicates = cursor.fetchall()
            if duplicates:
                self.stdout.write(self.style.WARNING(f"⚠️ Doublons trouvés dans la table de liaison:"))
                for dup in duplicates:
                    self.stdout.write(f"  - SocialApp {dup[0]}, Site {dup[1]}: {dup[2]} fois")
            else:
                self.stdout.write(self.style.SUCCESS("✓ Pas de doublons dans la table de liaison"))
            
            # Toutes les liaisons
            cursor.execute("""
                SELECT id, socialapp_id, site_id
                FROM socialaccount_socialapp_sites
                ORDER BY socialapp_id, site_id
            """)
            all_links = cursor.fetchall()
            self.stdout.write(f"\nToutes les liaisons ({len(all_links)}):")
            for link in all_links:
                cursor.execute("SELECT provider FROM socialaccount_socialapp WHERE id = %s", [link[1]])
                provider = cursor.fetchone()
                provider_name = provider[0] if provider else "UNKNOWN"
                self.stdout.write(f"  - Link ID: {link[0]}, App: {link[1]} ({provider_name}), Site: {link[2]}")

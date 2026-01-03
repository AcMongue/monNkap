from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Vérifie en profondeur la base de données pour les applications sociales'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # 1. Vérifier toutes les applications sociales
            self.stdout.write("=== TABLE socialaccount_socialapp ===")
            cursor.execute("""
                SELECT id, provider, name, client_id 
                FROM socialaccount_socialapp 
                WHERE provider = 'google'
            """)
            apps = cursor.fetchall()
            for app in apps:
                self.stdout.write(f"ID: {app[0]}, Provider: {app[1]}, Name: {app[2]}, Client: {app[3][:20]}...")
            
            # 2. Vérifier la table de liaison sites
            self.stdout.write("\n=== TABLE socialaccount_socialapp_sites ===")
            cursor.execute("""
                SELECT socialapp_id, site_id 
                FROM socialaccount_socialapp_sites
            """)
            links = cursor.fetchall()
            for link in links:
                self.stdout.write(f"SocialApp ID: {link[0]}, Site ID: {link[1]}")
            
            # 3. Vérifier les sites
            self.stdout.write("\n=== TABLE django_site ===")
            cursor.execute("SELECT id, domain, name FROM django_site")
            sites = cursor.fetchall()
            for site in sites:
                self.stdout.write(f"ID: {site[0]}, Domain: {site[1]}, Name: {site[2]}")
            
            # 4. NETTOYER COMPLÈTEMENT
            self.stdout.write("\n=== NETTOYAGE COMPLET ===")
            
            # Supprimer toutes les liaisons
            cursor.execute("DELETE FROM socialaccount_socialapp_sites")
            deleted_links = cursor.rowcount
            self.stdout.write(f"✓ {deleted_links} liaisons supprimées")
            
            # Supprimer toutes les applications Google
            cursor.execute("DELETE FROM socialaccount_socialapp WHERE provider = 'google'")
            deleted_apps = cursor.rowcount
            self.stdout.write(f"✓ {deleted_apps} applications Google supprimées")
            
            # Recréer l'application Google
            self.stdout.write("\n=== CRÉATION ===")
            import os
            client_id = os.environ.get('GOOGLE_CLIENT_ID')
            client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                self.stdout.write(self.style.ERROR("✗ Variables GOOGLE_CLIENT_ID et GOOGLE_CLIENT_SECRET non définies"))
                return
            
            # Insérer la nouvelle application
            cursor.execute("""
                INSERT INTO socialaccount_socialapp (provider, name, client_id, secret, key, settings)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, ['google', 'Google', client_id, client_secret, '', '{}'])
            app_id = cursor.fetchone()[0]
            self.stdout.write(f"✓ Application créée (ID: {app_id})")
            
            # Lier au site 1
            cursor.execute("""
                INSERT INTO socialaccount_socialapp_sites (socialapp_id, site_id)
                VALUES (%s, %s)
            """, [app_id, 1])
            self.stdout.write(f"✓ Liée au site 1")
            
            # Vérification finale
            cursor.execute("SELECT COUNT(*) FROM socialaccount_socialapp WHERE provider = 'google'")
            count = cursor.fetchone()[0]
            self.stdout.write(f"\n=== RÉSULTAT FINAL ===")
            self.stdout.write(f"Applications Google: {count}")
            
            if count == 1:
                self.stdout.write(self.style.SUCCESS("✓✓✓ Configuration correcte!"))
            else:
                self.stdout.write(self.style.ERROR(f"✗✗✗ ERREUR: {count} applications"))

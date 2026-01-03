from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Count


class Command(BaseCommand):
    help = 'Détecte et affiche les emails en double dans la base de données'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Désactiver les comptes en double (garde le plus ancien)',
        )

    def handle(self, *args, **options):
        # Trouver les emails utilisés plusieurs fois
        duplicate_emails = (
            User.objects.values('email')
            .annotate(count=Count('email'))
            .filter(count__gt=1, email__isnull=False)
            .exclude(email='')
        )
        
        if not duplicate_emails:
            self.stdout.write(self.style.SUCCESS('✓ Aucun email en double trouvé!'))
            return
        
        self.stdout.write(self.style.WARNING(f'\n⚠️ {duplicate_emails.count()} email(s) en double trouvé(s):\n'))
        
        total_duplicates = 0
        for item in duplicate_emails:
            email = item['email']
            count = item['count']
            users = User.objects.filter(email=email).order_by('date_joined')
            
            self.stdout.write(f'\nEmail: {email} ({count} comptes)')
            for user in users:
                status = "✓ ACTIF" if user.is_active else "✗ DÉSACTIVÉ"
                oldest = " [PLUS ANCIEN]" if user == users.first() else ""
                self.stdout.write(f'  - Username: {user.username} | Créé: {user.date_joined.date()} | {status}{oldest}')
            
            total_duplicates += count - 1
        
        if options['fix']:
            self.stdout.write(self.style.WARNING('\n🔧 Mode correction activé...'))
            fixed = 0
            
            for item in duplicate_emails:
                email = item['email']
                users = User.objects.filter(email=email).order_by('date_joined')
                oldest = users.first()
                
                # Désactiver tous sauf le plus ancien
                for user in users[1:]:
                    if user.is_active:
                        user.is_active = False
                        user.save()
                        self.stdout.write(f'  ✓ Compte désactivé: {user.username}')
                        fixed += 1
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ {fixed} compte(s) en double désactivé(s)'))
            self.stdout.write(self.style.SUCCESS(f'Les utilisateurs concernés devront créer un nouveau compte avec un email différent.'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠️ {total_duplicates} compte(s) en double à traiter'))
            self.stdout.write('Pour les désactiver automatiquement, utilisez: python manage.py check_duplicate_emails --fix')

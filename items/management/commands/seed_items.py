# items/management/commands/seed_items.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from items.models import Item


class Command(BaseCommand):
    help = 'Seeds the database with sample lost & found items'

    def handle(self, *args, **options):
        # Get or create a demo user to own these items
        user, _ = User.objects.get_or_create(
            username='seed_demo_user',
            defaults={'email': 'demo@retrieva.app'}
        )

        # Remove old seed items (so you can re-run safely)
        deleted = Item.objects.filter(user=user).delete()
        self.stdout.write(f'Cleared old seed items: {deleted}')

        today = timezone.now().date()

        # ✅ Paste YOUR Cloudinary URLs here
        items = [
            {
                'type': 'lost',
                'category': 'Wallet',
                'name': 'Brown leather wallet',
                'description': 'Lost near Avenue Habib Bourguiba. Contains ID and cards. Reward offered.',
                'img_url': 'https://res.cloudinary.com/dylq9vfo/image/upload/v1789721503/emil-kalibradov-Zf80cYcxSFA-unsplash.jpg',
                'status': 'active',
                'lat': 36.8065,
                'long': 10.1815,
                'incident_date': today - timedelta(days=2),
  
            },
            {
                'type': 'found',
                'category': 'Phone',
                'name': 'Samsung Galaxy A54',
                'description': 'Found on a bench in Sfax city center. Black case with a crack on the screen.',
                'img_url': 'https://res.cloudinary.com/dylq9vfo/image/upload/v1789721053/shiwa-id-Uae7ouMw91A-unsplash.jpg',
                'status': 'active',
                'lat': 34.7406,
                'long': 10.7603,
                'incident_date': today - timedelta(days=1),
               
            },
            {
                'type': 'lost',
                'category': 'Keys',
                'name': 'Car keys with red keychain',
                'description': 'Lost somewhere between Sousse marina and the beach. Very sentimental value.',
                'img_url': '',  
                'status': 'active',
                'lat': 35.8256,
                'long': 10.6370,
                'incident_date': today - timedelta(days=5),
              
            },
            {
                'type': 'found',
                'category': 'Bag',
                'name': 'Brown backpack',
                'description': 'Found at Tunis-Carthage Airport, terminal 2. Handed to security, listed here for visibility.',
                'img_url': 'https://res.cloudinary.com/dylq9vfo/image/upload/v1789720978/wiser-by-the-mile-3o-X8WJOP5E-unsplash.jpg',
                'status': 'active',
                'lat': 36.8477,
                'long': 10.2284,
                'incident_date': today - timedelta(days=3),
               
            },
            {
                'type': 'lost',
                'category': 'Electronics',
                'name': 'Steam Deck',
                'description': 'Lost in a taxi between Ariana and Menzah. White case with a small dent.',
                'img_url': 'https://res.cloudinary.com/dylq9vfo/image/upload/v1789721597/alexander-andrews-WLAW-NGcMiw-unsplash.jpg',
                'status': 'active',
                'lat': 36.8662,
                'long': 10.1970,
                'incident_date': today - timedelta(days=7),
              
            },
            {
                'type': 'found',
                'category': 'Documents',
                'name': 'Tunisian national ID card',
                'description': 'Found on the ground near Monastir train station. Name partially visible.',
                'img_url': '',
                'status': 'active',
                'lat': 35.7773,
                'long': 10.8260,
                'incident_date': today - timedelta(days=1),
       
            },
            {
                        'type': 'found',
                        'category': 'Phone',
                        'name': 'IPhone 16',
                        'description': 'Found near Avenue Habib Bourguiba.',
                        'img_url': 'https://res.cloudinary.com/dylq9vfo/image/upload/v1789721644/igor-omilaev-X4S-G_Q9U9g-unsplash.jpg',
                        'status': 'active',
                        'lat': 36.8080,
                        'long': 10.1820,
                        'incident_date': today - timedelta(days=2),
          
             },
        ]

        for data in items:
            Item.objects.create(user=user, **data)

        self.stdout.write(
            self.style.SUCCESS(f'✅ Seeded {len(items)} sample items!')
        )
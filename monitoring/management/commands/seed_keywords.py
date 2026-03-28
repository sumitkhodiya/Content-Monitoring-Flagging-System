"""
Management command to seed initial keywords.
"""

from django.core.management.base import BaseCommand
from monitoring.models import Keyword


DEFAULT_KEYWORDS = [
    'python',
    'django',
    'automation',
    'data pipeline',
    'machine learning',
    'web development',
]


class Command(BaseCommand):
    help = 'Seed the database with default keywords'

    def handle(self, *args, **options):
        created_count = 0
        
        for keyword_name in DEFAULT_KEYWORDS:
            keyword, created = Keyword.objects.get_or_create(name=keyword_name)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created keyword: {keyword_name}')
                )
                created_count += 1
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Keyword already exists: {keyword_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n{created_count} new keywords created')
        )

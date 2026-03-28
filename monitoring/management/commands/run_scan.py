"""
Management command to run a content scan.
"""

from django.core.management.base import BaseCommand
from monitoring.services import ScanService


class Command(BaseCommand):
    help = 'Run a content scan against the specified source'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='mock',
            choices=['mock', 'newsapi'],
            help='Data source to scan from (default: mock)'
        )

    def handle(self, *args, **options):
        source = options['source']
        
        self.stdout.write(f'Starting scan for source: {source}...')
        
        try:
            stats = ScanService.run_scan(source)
            
            self.stdout.write(self.style.SUCCESS('\n✓ Scan completed successfully!\n'))
            self.stdout.write(f'  Content items processed: {stats["content_items_processed"]}')
            self.stdout.write(f'  Flags created: {stats["flags_created"]}')
            self.stdout.write(f'  Flags updated: {stats["flags_updated"]}')
            self.stdout.write(f'  Flags suppressed: {stats["flags_suppressed"]}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'✗ Scan failed: {str(e)}')
            )

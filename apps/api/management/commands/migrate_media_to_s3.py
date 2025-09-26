from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Migrate existing media files to S3'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually doing it',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if not hasattr(settings, 'AWS_ACCESS_KEY_ID') or not settings.AWS_ACCESS_KEY_ID:
            self.stdout.write(
                self.style.ERROR('AWS credentials not configured. Skipping migration.')
            )
            return

        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if not media_root or not os.path.exists(media_root):
            self.stdout.write(
                self.style.WARNING('No local media directory found. Nothing to migrate.')
            )
            return

        self.stdout.write(f'Scanning media directory: {media_root}')
        
        migrated_count = 0
        error_count = 0
        
        for root, dirs, files in os.walk(media_root):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, media_root)
                s3_path = f'media/{relative_path}'
                
                try:
                    if dry_run:
                        self.stdout.write(f'Would migrate: {relative_path} -> {s3_path}')
                    else:
                        # Check if file already exists in S3
                        if default_storage.exists(s3_path):
                            self.stdout.write(f'Skipping (already exists): {s3_path}')
                            continue
                        
                        # Upload to S3
                        with open(local_path, 'rb') as f:
                            default_storage.save(s3_path, f)
                        
                        self.stdout.write(f'Migrated: {relative_path} -> {s3_path}')
                    
                    migrated_count += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error migrating {relative_path}: {str(e)}')
                    )
                    error_count += 1

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Dry run complete. Would migrate {migrated_count} files.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Migration complete. Migrated {migrated_count} files, {error_count} errors.'
                )
            )

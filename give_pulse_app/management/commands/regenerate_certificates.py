from django.core.management.base import BaseCommand
from django.db.models import Q
from give_pulse_app.models import Donation
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Regenerate certificates for donations that are missing them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--donation-id',
            type=int,
            help='Regenerate certificate for a specific donation ID',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if certificate already exists',
        )

    def handle(self, *args, **options):
        donation_id = options.get('donation_id')
        force = options.get('force', False)
        
        if donation_id:
            # Regenerate for specific donation
            try:
                donation = Donation.objects.get(id=donation_id)
                self.regenerate_certificate(donation, force)
            except Donation.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Donation {donation_id} not found')
                )
        else:
            # Regenerate for all donations missing certificates
            if force:
                donations = Donation.objects.all()
                self.stdout.write('Regenerating certificates for ALL donations...')
            else:
                donations = Donation.objects.filter(
                    Q(certificate_file__isnull=True) | Q(certificate_file='')
                )
                self.stdout.write(f'Found {donations.count()} donations without certificates')
            
            success_count = 0
            error_count = 0
            
            for donation in donations:
                try:
                    self.regenerate_certificate(donation, force)
                    success_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing donation {donation.id}: {e}')
                    )
                    error_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Completed: {success_count} successful, {error_count} errors'
                )
            )

    def regenerate_certificate(self, donation, force=False):
        """Regenerate certificate for a specific donation"""
        
        # Check if certificate already exists and we're not forcing regeneration
        if not force and donation.certificate_file and donation.certificate_file.name:
            # Verify the file actually exists
            file_path = os.path.join(settings.MEDIA_ROOT, donation.certificate_file.name)
            if os.path.exists(file_path):
                self.stdout.write(f'Donation {donation.id} already has certificate, skipping...')
                return
        
        self.stdout.write(f'Generating certificate for donation {donation.id}...')
        
        try:
            # Generate certificate
            donation.generate_certificate()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully generated certificate for donation {donation.id}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to generate certificate for donation {donation.id}: {e}')
            )
            raise

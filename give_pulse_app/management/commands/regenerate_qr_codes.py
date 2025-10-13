from django.core.management.base import BaseCommand
from django.db.models import Q
from give_pulse_app.models import DonationAppointment
import qrcode
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Regenerate QR code images for appointments that are missing them'

    def add_arguments(self, parser):
        parser.add_argument(
            '--appointment-id',
            type=int,
            help='Regenerate QR code for a specific appointment ID',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force regeneration even if QR code already exists',
        )

    def handle(self, *args, **options):
        appointment_id = options.get('appointment_id')
        force = options.get('force', False)
        
        if appointment_id:
            # Regenerate for specific appointment
            try:
                appointment = DonationAppointment.objects.get(id=appointment_id)
                self.regenerate_qr_code(appointment, force)
            except DonationAppointment.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Appointment {appointment_id} not found')
                )
        else:
            # Regenerate for all appointments missing QR codes
            if force:
                appointments = DonationAppointment.objects.all()
                self.stdout.write('Regenerating QR codes for ALL appointments...')
            else:
                appointments = DonationAppointment.objects.filter(
                    Q(qr_code_image__isnull=True) | Q(qr_code_image='')
                )
                self.stdout.write(f'Found {appointments.count()} appointments without QR code images')
            
            success_count = 0
            error_count = 0
            
            for appointment in appointments:
                try:
                    self.regenerate_qr_code(appointment, force)
                    success_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing appointment {appointment.id}: {e}')
                    )
                    error_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Completed: {success_count} successful, {error_count} errors'
                )
            )

    def regenerate_qr_code(self, appointment, force=False):
        """Regenerate QR code for a specific appointment"""
        
        # Check if QR code already exists and we're not forcing regeneration
        if not force and appointment.qr_code_image and appointment.qr_code_image.name:
            self.stdout.write(f'Appointment {appointment.id} already has QR code, skipping...')
            return
        
        if not appointment.qr_code_data:
            raise Exception('No QR code data available')
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(appointment.qr_code_data)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color='black', back_color='white')
        qr_filename = f'qr_appointment_{appointment.id}.png'
        qr_path = os.path.join(settings.MEDIA_ROOT, 'qr_codes', qr_filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        
        # Save QR code image
        qr_image.save(qr_path)
        
        # Update appointment with QR code image path
        appointment.qr_code_image.name = f'qr_codes/{qr_filename}'
        appointment.save()
        
        # Verify the file was created
        if not os.path.exists(qr_path):
            raise Exception(f'QR code file was not created at {qr_path}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated QR code for appointment {appointment.id}')
        )

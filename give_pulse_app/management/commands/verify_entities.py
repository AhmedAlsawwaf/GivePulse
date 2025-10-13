from django.core.management.base import BaseCommand
from django.db import transaction
from give_pulse_app.models import Hospital, Staff


class Command(BaseCommand):
    help = 'Verify or unverify hospitals and staff members'

    def add_arguments(self, parser):
        parser.add_argument(
            '--action',
            choices=['verify', 'unverify'],
            required=True,
            help='Action to perform: verify or unverify'
        )
        parser.add_argument(
            '--type',
            choices=['hospital', 'staff', 'all'],
            required=True,
            help='Type of entity to process'
        )
        parser.add_argument(
            '--id',
            type=int,
            help='Specific ID to process (optional)'
        )
        parser.add_argument(
            '--hospital-id',
            type=int,
            help='Hospital ID for staff verification (optional)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force the action without confirmation'
        )

    def handle(self, *args, **options):
        action = options['action']
        entity_type = options['type']
        entity_id = options.get('id')
        hospital_id = options.get('hospital_id')
        force = options['force']

        with transaction.atomic():
            if entity_type == 'hospital':
                self.handle_hospitals(action, entity_id, force)
            elif entity_type == 'staff':
                self.handle_staff(action, entity_id, hospital_id, force)
            elif entity_type == 'all':
                self.handle_hospitals(action, entity_id, force)
                self.handle_staff(action, entity_id, hospital_id, force)

    def handle_hospitals(self, action, entity_id, force):
        """Handle hospital verification/unverification"""
        if entity_id:
            try:
                hospital = Hospital.objects.get(id=entity_id)
                hospitals = [hospital]
            except Hospital.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Hospital with ID {entity_id} not found')
                )
                return
        else:
            hospitals = Hospital.objects.all()

        if not force and not entity_id:
            count = hospitals.count()
            confirm = input(f'Are you sure you want to {action} {count} hospitals? (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write('Operation cancelled.')
                return

        updated_count = 0
        for hospital in hospitals:
            if action == 'verify':
                hospital.is_verified = True
                hospital.save()
                updated_count += 1
                self.stdout.write(f'Verified hospital: {hospital.name}')
            else:
                hospital.is_verified = False
                hospital.save()
                updated_count += 1
                self.stdout.write(f'Unverified hospital: {hospital.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully {action}ed {updated_count} hospitals')
        )

    def handle_staff(self, action, entity_id, hospital_id, force):
        """Handle staff verification/unverification"""
        staff_queryset = Staff.objects.all()

        if entity_id:
            try:
                staff = Staff.objects.get(id=entity_id)
                staff_queryset = [staff]
            except Staff.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Staff with ID {entity_id} not found')
                )
                return
        elif hospital_id:
            try:
                hospital = Hospital.objects.get(id=hospital_id)
                staff_queryset = Staff.objects.filter(hospital=hospital)
            except Hospital.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Hospital with ID {hospital_id} not found')
                )
                return

        if not force and not entity_id:
            count = staff_queryset.count()
            confirm = input(f'Are you sure you want to {action} {count} staff members? (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write('Operation cancelled.')
                return

        updated_count = 0
        for staff in staff_queryset:
            if action == 'verify':
                staff.is_verified = True
                staff.save()
                updated_count += 1
                self.stdout.write(f'Verified staff: {staff.user.first_name} {staff.user.last_name}')
            else:
                staff.is_verified = False
                staff.save()
                updated_count += 1
                self.stdout.write(f'Unverified staff: {staff.user.first_name} {staff.user.last_name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully {action}ed {updated_count} staff members')
        )

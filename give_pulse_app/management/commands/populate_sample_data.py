"""
Django management command to populate the database with sample data for testing
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from give_pulse_app.models import User, Donor, Staff, Hospital, City, Governorate, BloodRequest, Match, DonationAppointment, Donation


class Command(BaseCommand):
    help = 'Populate the database with sample data for testing leaderboard and other features'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create governorates if they don't exist
        governorates_data = ['Cairo', 'Alexandria', 'Giza', 'Luxor']
        governorates = {}
        for gov_name in governorates_data:
            governorate, created = Governorate.objects.get_or_create(name=gov_name)
            governorates[gov_name] = governorate
            if created:
                self.stdout.write(f'Created governorate: {governorate.name}')
        
        # Create cities if they don't exist
        cities_data = [
            {'name': 'Cairo', 'governorate': governorates['Cairo']},
            {'name': 'Alexandria', 'governorate': governorates['Alexandria']},
            {'name': 'Giza', 'governorate': governorates['Giza']},
            {'name': 'Luxor', 'governorate': governorates['Luxor']},
        ]
        
        cities = {}
        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                name=city_data['name'],
                defaults={'governorate': city_data['governorate']}
            )
            cities[city_data['name']] = city
            if created:
                self.stdout.write(f'Created city: {city.name}')
        
        # Create hospitals if they don't exist
        hospitals_data = [
            {'name': 'Cairo University Hospital', 'city': cities['Cairo']},
            {'name': 'Alexandria Medical Center', 'city': cities['Alexandria']},
            {'name': 'Giza General Hospital', 'city': cities['Giza']},
            {'name': 'Luxor Hospital', 'city': cities['Luxor']},
        ]
        
        hospitals = {}
        for hospital_data in hospitals_data:
            hospital, created = Hospital.objects.get_or_create(
                name=hospital_data['name'],
                defaults={'city': hospital_data['city']}
            )
            hospitals[hospital_data['name']] = hospital
            if created:
                self.stdout.write(f'Created hospital: {hospital.name}')
        
        # Create sample users and donors
        donors_data = [
            {
                'first_name': 'Ahmed', 'last_name': 'Hassan', 'email': 'ahmed@example.com',
                'phone': '01012345678', 'city': cities['Cairo'], 'abo': 'O', 'rh': '+',
                'donation_count': 5
            },
            {
                'first_name': 'Sarah', 'last_name': 'Mohamed', 'email': 'sarah@example.com',
                'phone': '01012345679', 'city': cities['Alexandria'], 'abo': 'AB', 'rh': '-',
                'donation_count': 3
            },
            {
                'first_name': 'Omar', 'last_name': 'Ali', 'email': 'omar@example.com',
                'phone': '01012345680', 'city': cities['Giza'], 'abo': 'B', 'rh': '+',
                'donation_count': 7
            },
            {
                'first_name': 'Fatima', 'last_name': 'Ibrahim', 'email': 'fatima@example.com',
                'phone': '01012345681', 'city': cities['Luxor'], 'abo': 'A', 'rh': '-',
                'donation_count': 4
            },
            {
                'first_name': 'Mahmoud', 'last_name': 'Khalil', 'email': 'mahmoud@example.com',
                'phone': '01012345682', 'city': cities['Cairo'], 'abo': 'O', 'rh': '+',
                'donation_count': 6
            },
        ]
        
        donors = {}
        for donor_data in donors_data:
            # Create user
            user, created = User.objects.get_or_create(
                email=donor_data['email'],
                defaults={
                    'first_name': donor_data['first_name'],
                    'last_name': donor_data['last_name'],
                    'phone': donor_data['phone'],
                    'password': 'pbkdf2_sha256$600000$dummy$dummy'  # Dummy password
                }
            )
            
            if created:
                self.stdout.write(f'Created user: {user.first_name} {user.last_name}')
            
            # Create donor profile
            donor, created = Donor.objects.get_or_create(
                user=user,
                defaults={
                    'abo': donor_data['abo'],
                    'rh': donor_data['rh'],
                    'city': donor_data['city'],
                    'eligibility_consent': True
                }
            )
            
            donors[f"{donor_data['first_name']} {donor_data['last_name']}"] = {
                'donor': donor,
                'donation_count': donor_data['donation_count']
            }
        
        # Create a staff member to create blood requests
        staff_user, created = User.objects.get_or_create(
            email='staff@example.com',
            defaults={
                'first_name': 'Hospital',
                'last_name': 'Staff',
                'phone': '01000000000',
                'password': 'pbkdf2_sha256$600000$dummy$dummy'
            }
        )
        
        if created:
            self.stdout.write(f'Created staff user: {staff_user.first_name} {staff_user.last_name}')
        
        staff, created = Staff.objects.get_or_create(
            user=staff_user,
            defaults={'hospital': hospitals['Cairo University Hospital']}
        )
        
        # Create sample blood requests and completed donations
        for donor_name, donor_info in donors.items():
            donor = donor_info['donor']
            donation_count = donor_info['donation_count']
            
            # Create blood requests and matches for this donor
            for i in range(donation_count):
                # Create blood request
                blood_request = BloodRequest.objects.create(
                    hospital=hospitals['Cairo University Hospital'],
                    created_by=staff,
                    abo=donor.abo,
                    rh=donor.rh,
                    units_requested=1,
                    city=donor.city,
                    deadline_at=timezone.now() + timedelta(days=7),
                    notes=f'Sample request for {donor.user.first_name}',
                    created_at=timezone.now() - timedelta(days=30-i*5)
                )
                
                # Create match
                match = Match.objects.create(
                    blood_request=blood_request,
                    donor=donor,
                    status='completed',
                    created_at=timezone.now() - timedelta(days=30-i*5),
                    accepted_at=timezone.now() - timedelta(days=29-i*5),
                    donated_at=timezone.now() - timedelta(days=28-i*5)
                )
                
                # Create donation appointment
                appointment = DonationAppointment.objects.create(
                    match=match,
                    window_start=timezone.now() - timedelta(days=28-i*5),
                    window_end=timezone.now() - timedelta(days=28-i*5) + timedelta(hours=1)
                )
                
                # Create donation record
                Donation.objects.create(
                    match=match,
                    confirmed_by=staff,
                    units=1
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data with {len(donors)} donors and their donation history!'
            )
        )

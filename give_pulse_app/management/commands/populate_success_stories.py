"""
Django management command to populate the database with sample success stories
"""

from django.core.management.base import BaseCommand
from give_pulse_app.models import SuccessStory


class Command(BaseCommand):
    help = 'Populate the database with sample success stories'

    def handle(self, *args, **options):
        # Clear existing success stories
        SuccessStory.objects.all().delete()
        self.stdout.write('Cleared existing success stories.')

        # Sample success stories
        stories_data = [
            {
                'title': "Ahmed's Life-Saving Journey",
                'donor_name': 'Ahmed Hassan',
                'story_text': 'Ahmed has been donating blood for over 5 years. His O+ blood type has helped save countless lives, including emergency surgery patients and accident victims. He believes that every donation is a chance to make a difference.',
                'image_url': 'https://i.pravatar.cc/150?img=1',
                'display_order': 1,
                'is_published': True
            },
            {
                'title': "Sarah's Story of Hope",
                'donor_name': 'Sarah Mohamed',
                'story_text': 'Sarah started donating blood after her father needed multiple transfusions during his cancer treatment. She has donated 12 times and continues to encourage others to join the cause. Her AB- blood type is rare and highly needed.',
                'image_url': 'https://i.pravatar.cc/150?img=2',
                'display_order': 2,
                'is_published': True
            },
            {
                'title': "Omar's Regular Commitment",
                'donor_name': 'Omar Ali',
                'story_text': 'Omar has been a regular donor for 8 years, donating every 3 months without fail. His B+ blood has been used in over 20 successful surgeries. He says donating blood is the easiest way to save a life.',
                'image_url': 'https://i.pravatar.cc/150?img=3',
                'display_order': 3,
                'is_published': True
            },
            {
                'title': "Fatima's Emergency Response",
                'donor_name': 'Fatima Ibrahim',
                'story_text': 'When a major accident occurred in her city, Fatima was one of the first to respond to the emergency blood drive. Her A- blood type helped save 3 lives that day. She now volunteers at blood drives to help others.',
                'image_url': 'https://i.pravatar.cc/150?img=4',
                'display_order': 4,
                'is_published': True
            },
            {
                'title': "Mahmoud's Family Tradition",
                'donor_name': 'Mahmoud Khalil',
                'story_text': 'Mahmoud comes from a family of blood donors. His father, mother, and siblings all donate regularly. Together, they have contributed over 100 donations. He believes it\'s a family responsibility to help others.',
                'image_url': 'https://i.pravatar.cc/150?img=5',
                'display_order': 5,
                'is_published': True
            },
            {
                'title': "Nour's Young Donor Spirit",
                'donor_name': 'Nour Abdel Rahman',
                'story_text': 'At just 18, Nour became one of our youngest regular donors. She started donating as soon as she was eligible and has already helped save 5 lives. She encourages her friends to join the donor community.',
                'image_url': 'https://i.pravatar.cc/150?img=6',
                'display_order': 6,
                'is_published': True
            }
        ]

        # Create success stories
        created_count = 0
        for story_data in stories_data:
            story, created = SuccessStory.objects.get_or_create(
                title=story_data['title'],
                defaults=story_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created: {story.title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} success stories!'
            )
        )


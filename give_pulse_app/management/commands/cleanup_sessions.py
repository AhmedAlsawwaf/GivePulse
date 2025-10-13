"""
Django management command to clean up invalid sessions
"""

from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone


class Command(BaseCommand):
    help = 'Clean up invalid sessions with non-existent users'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up invalid sessions...')
        
        # Get all active sessions
        active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
        total_sessions = active_sessions.count()
        cleaned_count = 0
        
        for session in active_sessions:
            try:
                session_data = session.get_decoded()
                user_id = session_data.get('user_id')
                
                if user_id:
                    # Check if user exists
                    try:
                        user = User.objects.get(pk=user_id)
                        self.stdout.write(f'Valid session: {session.session_key[:8]}... - User: {user.first_name} {user.last_name}')
                    except User.DoesNotExist:
                        self.stdout.write(f'Invalid session: {session.session_key[:8]}... - User ID {user_id} does not exist - DELETING')
                        session.delete()
                        cleaned_count += 1
                else:
                    # Session without user_id - keep it (might be anonymous)
                    pass
                    
            except Exception as e:
                self.stdout.write(f'Error processing session {session.session_key[:8]}...: {e} - DELETING')
                session.delete()
                cleaned_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Cleanup completed! Processed {total_sessions} sessions, cleaned up {cleaned_count} invalid sessions.'
            )
        )


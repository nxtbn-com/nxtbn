from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Initializes the nxtbn project by populating predefined collections and categories'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting nxtbn initialization...'))

        # Call the populate_predefined_collection command
        call_command('populate_predefined_collection')
        self.stdout.write(self.style.SUCCESS('Successfully populated predefined collections.'))

        # Call the populate_predefined_category command
        call_command('populate_predefined_category')
        self.stdout.write(self.style.SUCCESS('Successfully populated predefined categories.'))

        self.stdout.write(self.style.SUCCESS('nxtbn initialization completed successfully.'))

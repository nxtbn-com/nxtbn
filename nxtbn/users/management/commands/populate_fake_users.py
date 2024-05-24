
from django.core.management.base import BaseCommand, CommandError
from users.models import User
from tqdm import tqdm
from users.tests import UserFactory

class Command(BaseCommand):
    help = 'Generate Fake  user'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, nargs='?', default=100)

    def handle(self, *args, **options):
        for i in tqdm(range(options['count'])):
            try:
                user = UserFactory.create()
            except Exception:
                continue
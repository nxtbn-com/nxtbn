import time

from django.db import connections
from django.db.utils import OperationalError # db exception
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Script to pause execuation until django database is ready"""

    def handle(self, *args, **options):
        wait = 1
        self.stdout.write("Waiting for database ready...")
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError: # db exception
                self.stdout.write("Database not ready yet, waiting {} second...".format(wait))
                time.sleep(wait)

        self.stdout.write(self.style.SUCCESS('Database connected successfully!'))

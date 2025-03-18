
from django.core.management.base import BaseCommand
from process_watcher.process_watcher import run


class Command(BaseCommand):
    help = "Starts process reader to monitor processes and store in the database"
    def handle(self, *args, **kwargs):
        run(self)



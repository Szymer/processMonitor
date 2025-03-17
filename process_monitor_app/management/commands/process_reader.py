
from django.core.management.base import BaseCommand
import time
import psutil
from process_monitor_app.models import Process
from process_watcher.process_watcher import ProcessReader
# from process_monitor_app.process_watcher import ProcessReader

class Command(BaseCommand):
    help = "Starts process reader to monitor processes and store in the database"
    def handle(self, *args, **kwargs):
        pr = ProcessReader()
        self.stdout.write(self.style.SUCCESS("Starting ProcessReader..."))
        while True:
            processes = pr.process_classification(psutil.process_iter())

            for process in processes['to_add']:
                try:
                    pr.send_process_to_db(process)
                except Exception as e:
                    self.stdout.write(f"Error processing {process.pid}: {e}")

            for process in processes['to_delete']:
                    pr.delete_process_from_db(process)
                    del pr.cache[process]
                    # self.stdout.write(f"Removed process {pid} from cache.")

            self.stdout.write('Sleeping for 5 seconds...')
            time.sleep(5)




import sys
import threading
import time

from django.apps import AppConfig


class ProcessMonitorAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "process_monitor_app"

    def ready(self):
        """Starts process_reader after Django starts"""
        if "runserver" in sys.argv:
            print("Uruchamianie ProcessReader...")

            threading.Thread(target=self.start_process_reader, daemon=True).start()

    def start_process_reader(self):
        """Runs process_reader in a separate thread"""
        time.sleep(5)
        from process_monitor_app.management.commands.process_reader import Command

        Command().handle()

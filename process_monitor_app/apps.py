import sys
import threading
import time
from django.apps import AppConfig


class ProcessMonitorAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'process_monitor_app'
    
    
    def ready(self):
        """Uruchamia process_reader po starcie Django"""
        if 'runserver' in sys.argv:  # Sprawdza, czy uruchomiono serwer
            print("Uruchamianie ProcessReader...")
            
            threading.Thread(target=self.start_process_reader, daemon=True).start()
    
    
    def start_process_reader(self):
        """Uruchamia process_reader w osobnym wątku"""
        time.sleep(5)  # Krótka pauza, by uniknąć błędów inicjalizacji
        
        from process_monitor_app.management.commands.process_reader import Command
        Command().handle()
  
    
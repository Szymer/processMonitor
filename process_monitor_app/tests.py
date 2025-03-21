from django.test import TestCase
from django.utils.timezone import now

from process_monitor_app.models import Process, Snapshot, StoppedProcess, StoredProcess


class ProcessModelTest(TestCase):

    def test_create_process(self):
        """Testuje, czy Process po   prawnie się zapisuje do bazy danych"""
        process = Process.objects.create(
            PID=1234,
            name="Test Process",
            status="Running",
            start_time=now(),
            duration=5.5,
            memory_usage_MB=100.5,
            CPU_Usage_Percent=12.3,
        )

        self.assertIsNotNone(process.id)
        self.assertEqual(process.name, "Test Process")
        self.assertEqual(str(process), "Test Process (PID: 1234)")

    def test_process_pid_is_integer(self):
        """Sprawdza, czy PID to liczba całkowita"""
        process = Process.objects.create(
            PID=5678,
            name="Another Process",
            status="Stopped",
            start_time=now(),
            duration=10,
            memory_usage_MB=200,
            CPU_Usage_Percent=50,
        )
        self.assertIsInstance(process.PID, int)


class SnapshotModelTest(TestCase):

    def test_create_snapshot(self):
        """Sprawdza, czy Snapshot poprawnie się tworzy"""
        snapshot = Snapshot.objects.create(author="Admin")
        self.assertIsNotNone(snapshot.id)
        self.assertIn("Snapshot", str(snapshot))


class StoredProcessModelTest(TestCase):

    def test_stored_process_links_to_snapshot(self):
        """Testuje relację ForeignKey między StoredProcess a Snapshot"""
        snapshot = Snapshot.objects.create(author="Admin")
        stored_process = StoredProcess.objects.create(
            PID=4321,
            name="Stored Process",
            status="Paused",
            start_time=now(),
            duration=3.2,
            memory_usage_MB=50,
            CPU_Usage_Percent=5,
            snapshot=snapshot,
        )

        self.assertEqual(stored_process.snapshot, snapshot)
        self.assertEqual(stored_process.snapshot.author, "Admin")


class StoppedProcessModelTest(TestCase):

    def test_create_stopped_process(self):

        stopped = StoppedProcess.objects.create(author="User123", name="Stopped App")

        self.assertIsNotNone(stopped.id)
        self.assertIn("stopped by User123", str(stopped))

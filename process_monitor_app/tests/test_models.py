import pytest
from django.utils.timezone import now
from process_monitor_app.models import Process, Snapshot, StoredProcess, StoppedProcess


@pytest.mark.django_db
def test_create_process():

    process = Process.objects.create(
        PID=1234,
        name="Test Process",
        status="Running",
        start_time=now(),
        duration=5.5,
        memory_usage_MB=100.5,
        CPU_Usage_Percent=12.3,
    )

    assert process.id is not None
    assert process.name == "Test Process"
    assert str(process) == "Test Process (PID: 1234)"


@pytest.mark.django_db
def test_process_pid_is_integer():
    process = Process.objects.create(
        PID=5678,
        name="Another Process",
        status="Stopped",
        start_time=now(),
        duration=10,
        memory_usage_MB=200,
        CPU_Usage_Percent=50,
    )
    assert isinstance(process.PID, int)


@pytest.mark.django_db
def test_create_snapshot():
    """Sprawdza, czy Snapshot zapisuje się poprawnie"""
    snapshot = Snapshot.objects.create(author="Admin")
    assert snapshot.id is not None
    assert "Snapshot" in str(snapshot)


@pytest.mark.django_db
def test_stored_process_links_to_snapshot():
    """Sprawdza relację ForeignKey między StoredProcess i Snapshot"""
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
    assert stored_process.snapshot == snapshot
    assert stored_process.snapshot.author == "Admin"


@pytest.mark.django_db
def test_create_stopped_process():
    """Testuje, czy StoppedProcess poprawnie zapisuje się do bazy"""
    stopped = StoppedProcess.objects.create(author="User123", name="Stopped App")
    assert stopped.id is not None
    assert "stopped by User123" in str(stopped)

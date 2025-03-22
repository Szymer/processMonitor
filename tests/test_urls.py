import pytest
from django.urls import reverse, resolve
from process_monitor_app.views import ProcessListView, SnapshotDetailedView

@pytest.mark.django_db
def test_process_list_url():
  
    url = reverse("process_list")
    assert resolve(url).func.view_class == ProcessListView

@pytest.mark.django_db
def test_snapshot_detail_url():

    url = reverse("snapshot_detail", args=[1])  
    assert resolve(url).func.view_class == SnapshotDetailedView

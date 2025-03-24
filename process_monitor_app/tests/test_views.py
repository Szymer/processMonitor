import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_process_list_view_access(client):
    """Sprawdza, czy niezalogowany użytkownik nie ma dostępu do listy procesów."""
    url = reverse("process_list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login/" in response.url


@pytest.mark.django_db
def test_process_list_view_authenticated_access(client, django_user_model):
    """Sprawdza, czy zalogowany użytkownik ma dostęp do listy procesów."""
    django_user_model.objects.create_user(username="testuser", password="password")
    client.login(username="testuser", password="password")
    url = reverse("process_list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_snap_list_view_access(client):
    """Sprawdza, czy niezalogowany użytkownik nie ma dostępu do listy procesów."""
    url = reverse("snapshot_list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login/" in response.url


@pytest.mark.django_db
def test_snap_list_view_authenticated_access(client, django_user_model):
    """Sprawdza, czy zalogowany użytkownik ma dostęp do listy procesów."""
    django_user_model.objects.create_user(username="testuser", password="password")
    client.login(username="testuser", password="password")
    url = reverse("snapshot_list")
    response = client.get(url)
    assert response.status_code == 200

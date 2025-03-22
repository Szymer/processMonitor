import pytest
from django.contrib.admin.sites import site
from process_monitor_app.models import Process

@pytest.mark.parametrize("model", [Process])
def test_models_registered(model):
    """Sprawdza, czy modele są zarejestrowane w Django Admin."""
    assert model in site._registry, f"{model.__name__} nie jest zarejestrowany w Django Admin"

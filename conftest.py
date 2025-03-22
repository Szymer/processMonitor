import pytest
from django.contrib.auth.models import User

@pytest.fixture
def test_user(db):
    return User.objects.create_user(username="testuser", password="password")

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


def create_test_user(**params):
    defaults = {
        "email": "test@example.com",
        "password": "testpass123",
    }
    defaults.update(params)
    # defaults["password"] = make_password(defaults.get("password"))
    
    return get_user_model().objects.create_user(**defaults)

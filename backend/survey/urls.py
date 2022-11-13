from django.urls import path, include
from rest_framework.schemas import get_schema_view

from .api import urlpatterns


urlpatterns = [
    path("api/", include(urlpatterns)),
    path("openapi/", get_schema_view(
        title="Your Project",
        description="API for all things …",
        version="1.0.0"
    ), name='openapi-schema'),
]

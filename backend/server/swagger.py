from django.urls import re_path
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version="v1",
   ),
   public=True,
   permission_classes=[AllowAny, ],
)


urlpatterns = [
    re_path(
        r"\.json$",
        schema_view.without_ui(cache_timeout=0),
        kwargs={"format": ".json"},
        name="schema-json",
    ),
    re_path(
        r"(/)?$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
]

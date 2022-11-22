from django.contrib import admin
from django.urls import path, re_path, include


urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/", include(api_urls)),
    re_path(r"^swagger", include("server.swagger")),
]

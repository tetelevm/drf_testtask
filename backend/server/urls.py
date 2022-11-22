from django.contrib import admin
from django.urls import path, re_path, include

from .drf import ProjectViewMeta


# initialize and create a list of url for all api
ProjectViewMeta.initialize()
api_urls = ProjectViewMeta.get_paths()


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(api_urls)),
    re_path(r"^swagger", include("server.swagger")),
]

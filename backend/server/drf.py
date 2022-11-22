from __future__ import annotations

from abc import ABC, ABCMeta
from typing import Type

from django.db.models import QuerySet
from django_filters import FilterSet
from django.urls import path
from rest_framework.views import APIView
from rest_framework.serializers import Serializer

from server.utils import camel_to_snake


__all__ = [
    "ProjectViewMeta",
    "ProjectView",
]


class ProjectViewMeta(ABCMeta):
    """
    A metaclass for all views in the project.
    Adds url for all api based on the class name, and also can import
    api from all applications in the project.
    And it stores a list of url-view relations.
    """

    _apis: dict[str, ProjectViewMeta] = dict()

    def __new__(mcs, name, bases, dct):
        if ABC not in bases:
            # creating a link for the api
            api_name = dct.get("url") or camel_to_snake(name.removesuffix("View"))
            if api_name in mcs._apis:
                raise ValueError(f"api with <{api_name}> url already exist")
            dct["url"] = api_name

        cls = super().__new__(mcs, name, bases, dct)

        if hasattr(cls, "url"):
            mcs._apis[cls.url] = cls

        return cls

    @classmethod
    def get_paths(mcs):
        """
        Generates a list of `path` for all api.
        """
        return [
            path(name, cls.as_view())
            for (name, cls) in mcs._apis.items()
        ]

    @staticmethod
    def initialize():
        """
        Imports all `api` modules/files from applications in
        INSTALLED_APPS (does not import django applications).
        It's made so that api in new applications are imported
        automatically without explicit importing.
        """
        from django.conf import settings
        apps = filter(
            lambda app: not app.startswith("django."),
            settings.INSTALLED_APPS
        )
        for app in apps:
            try:
                __import__(f"{app}.api")
            except ModuleNotFoundError:
                pass


class ProjectView(APIView, ABC, metaclass=ProjectViewMeta):
    """
    A parent class for all api of the project.
    """

    url: str
    serializer_class: Type[Serializer]
    queryset: QuerySet
    filter_class: Type[FilterSet] | None = None

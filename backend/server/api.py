from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken

from server.drf import ProjectView


__all__ = [
    "LoginView",
    "LogoutView",
]


class LoginView(ProjectView, ObtainAuthToken):
    """
    Authentication is done via login-password. Creates and returns an
    OAuth2 token that can be used as credentials.
    """


class LogoutView(ProjectView):
    """
    Api to logout. If the user is not logged in, nothing happens, if the
    user is logged in, it unlogins him (deletes tokens and the session).
    """

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.user or request.user.is_anonymous:
            return Response({"ok": True})

        try:
            # fails when authenticating via login/password
            request.user.auth_token.delete()
        except ObjectDoesNotExist:
            pass
        logout(request)

        return Response({"ok": True})

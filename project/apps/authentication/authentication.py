from rest_framework.authentication import TokenAuthentication
from apps.users.models import Token


class TokenOverride(TokenAuthentication):
    model = Token

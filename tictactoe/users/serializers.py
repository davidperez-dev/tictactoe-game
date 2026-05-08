from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Extends the default JWT payload with the user's roles.

    The resulting token includes:
        {
          "username": "david",
          "email": "davidperez.code@gmail.com",
          "roles": ["admin"]
        }

    The external web reads roles from the token exactly as it would
    with a Keycloak token (roles array in the payload).
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"]    = user.email
        token["roles"]    = list(user.groups.values_list("name", flat=True))
        return token

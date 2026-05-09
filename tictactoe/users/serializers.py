from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User, Group
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "email", "roles", "is_active"]

    def get_roles(self, obj):
        return list(obj.groups.values_list("name", flat=True))


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration. It validates the input data and creates a new user.
    """

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        username = validated_data["username"]
        password = validated_data["password"]

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Username already exists"})

        user = User.objects.create_user(username=username, password=password)

        default_role = "user"
        group, _ = Group.objects.get_or_create(name=default_role)
        user.groups.add(group)

        return user

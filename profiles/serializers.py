from djoser.serializers import (
    UserSerializer,
    UserCreateSerializer as BaseUserCreateSerializer,
)


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        fields = (
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
        )


class UserDetailSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ("id", "email", "username", "first_name", "last_name")

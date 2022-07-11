from lib2to3.pytree import Base
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer


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

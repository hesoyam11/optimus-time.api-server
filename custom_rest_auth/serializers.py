from django.contrib.auth import get_user_model
from rest_framework import serializers

USER_MODEL = get_user_model()

USERNAME_MIN_LENGTH = 5
USERNAME_MAX_LENGTH = 150
FIRST_NAME_MAX_LENGTH = 30
LAST_NAME_MAX_LENGTH = 150
PASSWORD_MIN_LENGTH = 8


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH
    )
    password = serializers.CharField(
        min_length=PASSWORD_MIN_LENGTH
    )


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(
        min_length=USERNAME_MIN_LENGTH,
        max_length=USERNAME_MAX_LENGTH
    )
    email = serializers.EmailField()
    first_name = serializers.CharField(
        max_length=FIRST_NAME_MAX_LENGTH,
        required=False
    )
    last_name = serializers.CharField(
        max_length=LAST_NAME_MAX_LENGTH,
        required=False
    )
    password = serializers.CharField(
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH
    )
    password_repeat = serializers.CharField(
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH
    )

    @staticmethod
    def _field_is_unique(field_name, value):
        kwargs = {field_name: value}
        try:
            USER_MODEL.objects.get(**kwargs)
        except USER_MODEL.DoesNotExist:
            return True
        return False

    def validate_username(self, username):
        if not self._field_is_unique('username', username):
            raise serializers.ValidationError(
                f'Username "{username}" is already in use.'
            )
        return username

    def validate_email(self, email):
        if not self._field_is_unique('email', email):
            raise serializers.ValidationError(
                f'Email "{email}" is already in use.'
            )
        return email

    def validate(self, data):
        if data['password'] != data['password_repeat']:
            raise serializers.ValidationError(
                "The two password fields didn't match."
            )
        return data

    def create(self, validated_data):
        user = USER_MODEL(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH
    )
    new_password_repeat = serializers.CharField(
        write_only=True,
        min_length=PASSWORD_MIN_LENGTH
    )

    def validate(self, data):
        if data['new_password'] != data['new_password_repeat']:
            raise serializers.ValidationError(
                "The two password fields didn't match."
            )
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = USER_MODEL
        fields = ('pk', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('pk', 'email')

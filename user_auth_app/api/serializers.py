from rest_framework import serializers
from django.contrib.auth.models import User
from coderr_app.models import Profile

class RegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.

    Fields:
        - username: Unique username
        - email: Unique email address
        - password: Password (write-only)
        - repeated_password: Password confirmation (write-only)
        - type: User type (ChoiceField from Profile.USER_TYPES,
                e.g., 'customer' or 'business')
        - first_name: Optional first name
        - last_name: Optional last name
    """
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=Profile.USER_TYPES)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        """
        Validates that the password and repeated_password fields match.

        Raises:
            ValidationError: If the passwords do not match.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def validate_username(self, value):
        """
        Ensures that the username is unique.

        Raises:
            ValidationError: If the username already exists.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        """
        Ensures that the email address is unique.

        Raises:
            ValidationError: If the email already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    
    def create(self, validated_data):
        """
        Creates a new Django User and an associated Profile.

        Steps:
            1. Remove repeated_password from validated data.
            2. Extract user type, first_name, and last_name.
            3. Create the User using create_user (handles password hashing).
            4. Create the associated Profile with the selected type.
            5. Return the created User instance.
        """
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name
        )

        Profile.objects.create(
            user=user,
            type=user_type
        )

        return user
from rest_framework import serializers
from django.contrib.auth.models import User
from coderr_app.models import Profile

class RegistrationSerializer(serializers.Serializer):
    """
    Serializer für Benutzerregistrierung.

    Felder:
    - username: eindeutiger Benutzername
    - email: eindeutige Email-Adresse
    - password: Passwort (write_only)
    - repeated_password: Passwort zur Bestätigung (write_only)
    - type: Benutzer-Typ (ChoiceField aus Profile.USER_TYPES, z.B. 'customer' oder 'business')
    - first_name: optionaler Vorname
    - last_name: optionaler Nachname
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
        Validiert, dass password und repeated_password übereinstimmen.
        """
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def validate_username(self, value):
        """
        Prüft, dass der Benutzername noch nicht existiert.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        """
        Prüft, dass die Email-Adresse noch nicht existiert.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    
    def create(self, validated_data):
        """
        Erstellt einen neuen Django User und ein zugehöriges Profile.

        Schritte:
        1. Entfernt repeated_password aus den Daten
        2. Extrahiert user_type, first_name und last_name
        3. Erstellt User mit create_user (inkl. Passwort-Hash)
        4. Erstellt zugehöriges Profile mit type und optionalen Namen
        5. Gibt das erstellte User-Objekt zurück
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
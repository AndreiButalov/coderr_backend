from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegistrationView(APIView):
    """
    API-View für Benutzerregistrierung.
    Berechtigungen: AllowAny
    Ablauf:
    1. Nimmt POST-Daten entgegen
    2. Serialisiert und validiert die Daten über RegistrationSerializer
    3. Erstellt User und Profile
    4. Gibt Token und Benutzerinformationen zurück
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class LoginView(APIView):
    """
    API-View für Benutzer-Login anhand von Username und Passwort.
    Berechtigungen: AllowAny
    Ablauf:
    1. POST-Daten 'username' und 'password' entgegennehmen
    2. Benutzer anhand username suchen
    3. Passwort überprüfen via authenticate
    4. Token erzeugen oder abrufen
    5. Rückgabe von Token und Benutzerinformationen
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        POST-Methode für Login.

        Request-Daten:
        - username
        - password

        Response (200):
        - token: Authentifizierungs-Token
        - username
        - email
        - user_id

        Response (400):
        - Fehler bei falschem Benutzer oder Passwort
        """
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Ungültige Anfragedaten'}, status=400)

        user = authenticate(username=user.username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_200_OK)

        return Response({'ok': False, 'error': 'Falsches Passwort'}, status=400)

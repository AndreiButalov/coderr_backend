from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegistrationView(APIView):
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
    API-View für Benutzer-Login.

    POST: Authentifiziert einen Benutzer anhand von Email und Passwort.
    - Bei Erfolg: Gibt Auth-Token, user_id, Email und Username zurück.
    - Bei Fehler: Fehlermeldung zurückgeben (E-Mail nicht gefunden oder falsches Passwort).
    
    Authentifiziert Benutzer und erstellt einen Token.

    Schritte:
    1. User anhand der Email suchen.
    2. Passwort prüfen mit authenticate().
    3. Token erstellen oder abrufen.
    4. Erfolgs- oder Fehlerantwort zurückgeben.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'ok': False, 'error': 'E-Mail nicht gefunden'}, status=400)

        user = authenticate(username=user.username, password=password)
        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email,
                'username': user.username
            }, status=200)

        return Response({'ok': False, 'error': 'Falsches Passwort'}, status=400)
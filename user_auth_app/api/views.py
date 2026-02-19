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
    API view for user registration.

    Permissions:
        - AllowAny (no authentication required)

    Workflow:
        1. Accepts POST data for registration
        2. Validates data using RegistrationSerializer
        3. Creates a new User and associated Profile
        4. Returns authentication token and user information
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles POST requests for user registration.

        Request data:
            - username
            - email
            - password
            - repeated_password
            - type
            - first_name (optional)
            - last_name (optional)

        Response (201 Created):
            - token: authentication token
            - username
            - email
            - user_id

        Response (400 Bad Request):
            - serializer validation errors
        """
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
    API view for user login using username and password.

    Permissions:
        - AllowAny (no authentication required)

    Workflow:
        1. Accepts POST data: 'username' and 'password'
        2. Verifies that the user exists
        3. Authenticates the user using Django's `authenticate`
        4. Retrieves or creates a token for the user
        5. Returns token and user information
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handles POST requests for user login.

        Request data:
            - username
            - password

        Response (200 OK):
            - token: authentication token
            - username
            - email
            - user_id

        Response (400 Bad Request):
            - error: invalid username or password
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

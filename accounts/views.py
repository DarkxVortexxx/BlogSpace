from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from blog.models import Profile
from .serializers import ProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from .serializers import RegisterSerializer


# Get CSRF Cookie
@ensure_csrf_cookie
def csrf_token(request):
    from django.http import JsonResponse
    return JsonResponse({"message": "CSRF cookie set"})


# User Registration
@method_decorator(csrf_protect, name='dispatch')
class RegisterView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            login(request._request, user)

            return Response({
                "message": "Registration successful!",
                "username": user.username
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# User Login
@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(
            request._request,
            username=username,
            password=password
        )

        if user is not None:
            login(request._request, user)

            return Response({
                "message": "Login successful!",
                "username": user.username
            })

        return Response({
            "error": "Invalid username or password"
        }, status=status.HTTP_400_BAD_REQUEST)


# User Logout
@method_decorator(csrf_protect, name='dispatch')
class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        logout(request._request)

        return Response({
            "message": "Logged out successfully!"
        })


# Current Logged-in User
class CurrentUserView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "username": request.user.username,
            "email": request.user.email,
            "authenticated": True
        })

# USER PROFILE API


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = Profile.objects.get_or_create(
            user=request.user
        )

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile, created = Profile.objects.get_or_create(
            user=request.user
        )

        serializer = ProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

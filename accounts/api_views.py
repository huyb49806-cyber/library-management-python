from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from urllib.parse import urlencode

from rest_framework import generics, status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .api_serializers import (
    AdminUserSerializer,
    MeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
)
from .models import UserProfile

User = get_user_model()


class IsAdminOperator(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (
                user.is_staff
                or user.groups.filter(name="Admin").exists()
            )
        )


class LoginView(APIView):
    permission_classes = ()

    def post(self, request):
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class RegisterView(generics.CreateAPIView):
    permission_classes = ()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {
            "detail": "Account created. You can now log in.",
            "user": response.data,
        }
        return response


class LogoutView(APIView):
    def post(self, request):
        refresh = request.data.get("refresh")

        if not refresh:
            return Response(
                {"detail": "refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            return Response(
                {"detail": "invalid refresh token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MeSerializer

    def get_object(self):
        UserProfile.objects.get_or_create(user=self.request.user)
        return self.request.user


class PasswordResetRequestView(APIView):
    permission_classes = ()

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            email__iexact=serializer.validated_data["email"],
            is_active=True,
        ).first()

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            query = urlencode({"uid": uid, "token": token})
            reset_link = f"{settings.PASSWORD_RESET_CONFIRM_URL}?{query}"

            send_mail(
                subject="Reset your library account password",
                message=f"Open this link to reset your password:\n{reset_link}",
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return Response({
            "detail": "If an account exists for this email, a reset link has been sent."
        })


class PasswordResetConfirmView(APIView):
    permission_classes = ()

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user_id = urlsafe_base64_decode(
                serializer.validated_data["uid"]
            ).decode()
            user = User.objects.get(pk=user_id, is_active=True)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):
            return Response(
                {"detail": "Invalid or expired reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = serializer.validated_data["token"]
        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_password = serializer.validated_data["new_password"]
        try:
            validate_password(new_password, user=user)
        except ValidationError as error:
            return Response(
                {"new_password": error.messages},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response({"detail": "Password reset successfully."})


class AdminUserListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAdminOperator,)
    serializer_class = AdminUserSerializer
    queryset = User.objects.all().order_by("username")


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminOperator,)
    serializer_class = AdminUserSerializer
    queryset = User.objects.all()

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user.borrowed_book_instances.filter(status="o").exists():
            return Response(
                {
                    "detail": "Không thể xóa tài khoản độc giả đang có sách mượn chưa trả. Vui lòng ghi nhận trả sách trước."
                },
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)
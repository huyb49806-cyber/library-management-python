from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import UserProfile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("student_code", "phone", "date_of_birth")


class MeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    groups = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "groups",
            "profile",
        )
        read_only_fields = (
            "id",
            "username",
            "is_active",
            "is_staff",
            "groups",
        )

    def validate_email(self, value):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        queryset = User.objects.filter(email__iexact=value)

        if user and user.pk:
            queryset = queryset.exclude(pk=user.pk)

        if queryset.exists():
            raise serializers.ValidationError("Email already exists.")

        return value

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})

        for field, value in validated_data.items():
            setattr(instance, field, value)

        instance.save()

        profile, _ = UserProfile.objects.get_or_create(user=instance)
        for field, value in profile_data.items():
            setattr(profile, field, value)
        profile.save()

        return instance


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False,
    )
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=Group.objects.all(),
        required=False,
    )

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "groups",
            "password",
        )
        read_only_fields = ("id",)

    def validate_email(self, value):
        queryset = User.objects.filter(email__iexact=value)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("Email already exists.")

        return value

    def validate(self, attrs):
        password = attrs.get("password")

        if self.instance is None and not password:
            raise serializers.ValidationError({
                "password": "Password is required when creating a user."
            })

        if password:
            candidate = User(
                username=attrs.get(
                    "username",
                    getattr(self.instance, "username", ""),
                ),
                email=attrs.get(
                    "email",
                    getattr(self.instance, "email", ""),
                ),
                first_name=attrs.get(
                    "first_name",
                    getattr(self.instance, "first_name", ""),
                ),
                last_name=attrs.get(
                    "last_name",
                    getattr(self.instance, "last_name", ""),
                ),
            )
            validate_password(password, user=candidate)

        return attrs

    def create(self, validated_data):
        groups = validated_data.pop("groups", [])
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        user.groups.set(groups)
        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop("groups", None)
        password = validated_data.pop("password", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)

        instance.save()

        if groups is not None:
            instance.groups.set(groups)

        return instance


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(min_length=8, write_only=True)
    student_code = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
    )
    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def validate(self, attrs):
        password = attrs["password"]
        password_confirm = attrs.pop("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })

        candidate = User(
            username=attrs["username"],
            email=attrs["email"],
            first_name=attrs["first_name"],
            last_name=attrs["last_name"],
        )
        validate_password(password, user=candidate)

        return attrs

    def create(self, validated_data):
        student_code = validated_data.pop("student_code", "") or None
        phone = validated_data.pop("phone", "")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        member_group, _ = Group.objects.get_or_create(name="Member")
        user.groups.add(member_group)

        UserProfile.objects.create(
            user=user,
            student_code=student_code,
            phone=phone,
        )

        return user
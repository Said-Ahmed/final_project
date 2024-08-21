from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Profile


class UserRegistrationSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False)
    password = serializers.CharField(
        write_only=True,
        max_length=64,
        required=True
    )
    password2 = serializers.CharField(
        write_only=True,
        max_length=64,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'photo')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('Passwords don\'t match.')
        return attrs

    def create(self, validated_data):
        del validated_data['password2']
        photo = None
        if 'photo' in validated_data:
            photo = validated_data.pop('photo')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, photo=photo)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'user', 'date_of_birth', 'photo']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    photo = serializers.ImageField(required=False)

    class Meta:
        model = Profile
        fields = '__all__'

    def update(self, instance, validated_data):
        user_data = {
            'username': validated_data.pop(
                'username', instance.user.username
            ),
            'email': validated_data.pop(
                'email', instance.user.email
            ),
        }
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = {
            'username': instance.user.username,
            'email': instance.user.email,
            'is_staff': instance.user.is_staff
        }
        return representation




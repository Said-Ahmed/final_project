from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from .permissions import IsOwnerOrReadOnly, IsOwner
from .serializers import UserRegistrationSerializer, ProfileSerializer, ProfileUpdateSerializer
from rest_framework import viewsets


@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        user_serializer = UserRegistrationSerializer(data=request.data)
        if user_serializer.is_valid():
            new_user = user_serializer.save()
            return Response(
                {
                    'username': new_user.username,
                    'message': 'User created successfully.'
                },
                status=status.HTTP_201_CREATED
            )
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = UsersPagination

    def get_permissions(self):
        if self.action in ['my_profile', 'update_profile', 'delete_profile']:
            return IsOwner(),
        elif self.action == 'destroy':
            return IsAdminUser(),
        else:
            return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'update_profile':
            return ProfileUpdateSerializer
        return ProfileSerializer

    def perform_destroy(self, instance):
        instance.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='my_profile', url_name='my_profile')
    def my_profile(self, request):
        profile = get_object_or_404(
            Profile,
            user=request.user
        )
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='update_profile', url_name='update_profile')
    def update_profile(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path='delete_profile', url_name='delete_profile')
    def delete_profile(self, request):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



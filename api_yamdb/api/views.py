from asyncio.windows_events import NULL
from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework import status, permissions, filters
from rest_framework.pagination import PageNumberPagination

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Review
from categories.models import Title

from .serializers import (
    ConfirmationCodeSerializer,
    UsersSerializer,
    JWTTokenSerializer,
    UsersSerializer,
)
from .serializers import (
    ReviewSerializer,
    CommentSerializer,
)
from .permissions import (
    IsAuthorOrReadOnlyPermission,
    IsAdmin,
    IsModerator,
    ReadOnlyPermission,
    OwnerPermission,
)
from users.models import User
from .permissions import (IsAdmin, IsAuthorOrReadOnlyPermission, IsModerator,
                          OwnerPermission, ReadOnlyPermission)
from .serializers import (CommentSerializer, ConfirmationCodeSerializer,
                          JWTTokenSerializer, ReviewSerializer,
                          UsersSerializer, UserMeSerializer)


@api_view(['POST'])
@permission_classes([AllowAny,])
def get_confirmation_code(request):
        serializer = ConfirmationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email = serializer.validated_data['email']
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Регистрация', f'Код подтверждения: {confirmation_code}',
            'admin@yambd', [email], fail_silently=False, )
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny,])
def get_token(request):
    serializer = JWTTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=serializer.data.get('username'))
    confirmation_code = serializer.data.get('confirmation_code')
    if not default_token_generator.check_token(user, confirmation_code):
        return Response(
            {"Неверный код подтверждения. Повторите попытку."},
            status=status.HTTP_400_BAD_REQUEST
        )
    return Response(
        {"token": str(RefreshToken.for_user(user).access_token)}
    )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    lookup_url_kwarg = 'username'
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'role',)
    permission_classes = [IsAdminUser | IsAdmin, IsAuthenticated,]
    pagination_class = PageNumberPagination
  
    def get_object(self):
        if self.kwargs['username'] == 'me':
            obj = self.request.user
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()
    def destroy(self, request, *args, **kwargs):
        if self.kwargs['username'] == 'me':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class UserView(APIView):
    @staticmethod
    def get(request):
        user = request.user
        serializer = UserMeSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def patch(request):
        user = request.user
        serializer = UserMeSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAdmin | IsModerator | IsAuthorOrReadOnlyPermission,
    ]
    pagination_class = LimitOffsetPagination

    def get_title_id(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title_id().reviews.all()

    def perform_create(self, serializer):
        title = self.get_title_id()
        serializer.save(author=self.request.user, title_id=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAdmin | IsModerator | IsAuthorOrReadOnlyPermission,
    ]
    pagination_class = LimitOffsetPagination

    def get_review_id(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review_id().comments.all()

    def perform_create(self, serializer):
        review = self.get_review_id()
        serializer.save(author=self.request.user, review_id=review)

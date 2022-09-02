from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from categories.models import Title
from reviews.models import Review
from users.models import User
from django.conf import settings

from .permissions import IsAdmin, IsAuthorOrReadOnlyPermission, IsAuthenticatedOrReadOnly, IsAuthorAdminModeratorOrReadOnly
from .serializers import (CommentSerializer, ConfirmationCodeSerializer,
                          JWTTokenSerializer, ReviewSerializer,
                          UsersSerializer)


@api_view(['POST'])
@permission_classes([AllowAny, ])
def get_confirmation_code(request):
    serializer = ConfirmationCodeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    email = serializer.validated_data['email']
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Регистрация', f'Код подтверждения: {confirmation_code}',
        settings.ADMIN_EMAIL, [email], fail_silently=False, )
    return Response(serializer.validated_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny, ])
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
#    permission_classes = [IsAuthenticatedOrReadOnly | IsAuthorAdminModeratorOrReadOnly, ]
    permission_classes = [IsAdminUser | IsAdmin, IsAuthenticated, ]
    pagination_class = PageNumberPagination

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrReadOnlyPermission, ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrReadOnlyPermission, ]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(author=self.request.user, review=review)

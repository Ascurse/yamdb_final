import logging
import sys

from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from reviews.models import Category, CustomUser, Genre, Review, Title

from .filters import TitlesFilter
from .methods import get_user_role
from .permissions import (IsAdminModeratorUserPermission, IsAdminOrReadOnly,
                          IsAdminUserCustom)
from .serializers import (CategorySerializer, CommentSerializer,
                          CustomUserSerializer, GenreSerializer,
                          MyTokenObtainSerializer, ReviewSerializer,
                          SignUpSerializer, TitleCreateSerializer,
                          TitleSerializer)

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s - строка %(lineno)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
handler.setFormatter(formatter)
logger.disabled = False
logger.debug('Логирование из views запущено')


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = 'username'
    trailing_slash = '/'

    def get_permissions(self):
        if 'getme' in self.action_map.values():
            logger.debug('Запущен эндпойнт me')
            logger.debug(self.request.auth)
            return (permissions.IsAuthenticated(),)
        if self.suffix == 'users-list' or 'user-detail':
            logger.debug('Запущен эндпойнт users-list или user-detail')
            return (IsAdminUserCustom(),)
        return False

    @action(detail=True, url_path='me', methods=['get', 'patch'])
    def getme(self, request):
        request_user = request.user
        custom_user = CustomUser.objects.get(username=request_user.username)
        logger.debug(request.auth)

        if request.method == 'GET':
            serializer = self.get_serializer(custom_user)
            logger.debug('Зафиксирован метод GET')
            logger.debug(dir(request))
            logger.debug(dir(self))
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            request_user_role = get_user_role(request.auth)
            logger.debug(f'User role: {request_user_role}')
            rd = request.data.copy()
            if 'role' in rd:
                del rd['role']
            if 'username' not in rd:
                rd['username'] = request_user.username
            if 'email' not in rd:
                rd['email'] = request_user.email
            serializer = self.get_serializer(custom_user, data=rd)
            if serializer.is_valid():
                serializer.save()
                user = serializer.instance
                if 'email' in rd or 'username' in rd:
                    username = user.username
                    confirmation_code = user.confirmation_code
                    # при запуске в производство поставить отправку по почте
                    logger.debug(
                        f'Объект {username}\n Его новый '
                        f'confirmation_code:{confirmation_code}.'
                    )
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_200_OK)
        return False

    def perform_create(self, serializer):
        rd = self.request.data
        role = rd.get('role')
        if role == 'admin':
            is_staff = True
        else:
            is_staff = False
        serializer.save(is_staff=is_staff)

    def perform_update(self, serializer):
        rd = self.request.data
        role = rd.get('role')
        if role == 'admin':
            is_staff = True
        else:
            is_staff = False
        serializer.save(is_staff=is_staff)
        user = serializer.instance
        if 'email' in rd or 'username' in rd:
            username = user.username
            confirmation_code = user.confirmation_code
            # при запуске в производство поставить отправку по почте
            logger.debug(
                f'Объект {username}\n Его новый '
                f'confirmation_code:{confirmation_code}.'
            )


class APISignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        logger.debug(request.data)
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            logger.debug('Валидация APISignupView пройдена')
            serializer.save(is_active=False)
            user = serializer.instance
            rd = request.data
            username = rd.get('username')
            email = rd.get('email')
            confirmation_code = user.confirmation_code
            mail_theme = 'Подтверждение регистрации пользователя'
            mail_text = (
                f'Здравствуйте!\n\n\tВы (или кто-то другой) '
                'запросили регистрацию на сайте YaMDB. '
                'Для подтверждения регистрации отправьте POST запрос '
                'на адрес: http://127.0.0.1/api/v1/auth/token/. '
                f'В теле запроса передайте имя пользователя {username} '
                f'по ключу "username" и код \n\n{confirmation_code}\n\n'
                f'по ключу "confirmation_code".'
            )
            mail_from = 'orel333app@gmail.com'
            mail_to = [email]
            send_mail(
                mail_theme,
                mail_text,
                mail_from,
                mail_to,
                fail_silently=False
            )
            logger.debug(confirmation_code)

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        rd = request.data.copy()
        logger.debug(f'View: request.data: {rd}')
        serializer = MyTokenObtainSerializer(data=rd)
        if serializer.is_valid():
            logger.debug('Serializer is valid')
            username = rd.get('username')
            user = get_object_or_404(CustomUser, username=username)
            user.is_active = True
            user.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all()
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TitlesFilter
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Пользователи оставляют к произведениям текстовые отзывы."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorUserPermission,)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Title.objects.none()
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Пользователи оставляют коментарии к отзывам."""
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorUserPermission,)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get('title_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            title_id=self.kwargs.get('title_id'),
            id=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)

import logging
import sys

import jwt
from api.methods import text_processor
from api.validators import validate_year
from api_yamdb.settings import SECRET_KEY
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
from rest_framework_simplejwt.tokens import AccessToken

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s - строка %(lineno)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
handler.setFormatter(formatter)
logger.disabled = False
logger.debug('Логирование из models запущено')

ROLE_CHOICES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
)


class CustomUserManager(BaseUserManager):
    def create_superuser(self, username, email, password, **other_fields):
        logger.debug('SuperUser is being initialized...')
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        if other_fields.get('is_staff') is not True:
            raise ValueError(
                '"is_staff" суперпользователя должно быть в режиме "True"'
            )
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                '"is_superuser" суперпользователя должно быть в режиме "True"'
            )
        logger.debug(
            f'Here are some other fields in parameters: {other_fields}'
        )
        if 'role' in other_fields:
            role = other_fields.get('role')
            del other_fields['role']
        else:
            role = 'admin'

        return self.create_user(
            username,
            email,
            role,
            password,
            **other_fields
        )

    def create_user(
        self,
        username,
        email,
        role='user',
        password=None,
        **other_fields
    ):
        logger.debug(f'Got role: {role}')
        logger.debug(f'Got password: {password}')
        logger.debug(f'Is_staff: {other_fields.get("is_staff")}')
        logger.debug(f'Is_superuser: {other_fields.get("is_superuser")}')
        logger.debug('Create user func was initiated')
        if not email:
            raise ValueError('Необходимо указать email')
        if not username:
            raise ValueError('Необходимо указать username')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            role=role,
            **other_fields
        )
        if role == 'admin':
            user.is_staff = True
            user.set_password(password)
        user.save()
        confirmation_code = user.confirmation_code
        token = user.token
        if user.is_superuser is True:
            first_line = f'Создан суперпользователь {username}.\n'
        else:
            first_line = f'Создан пользователь {username}.\n'
        # при запуске в производство поставить отправку по почте
        logger.debug(
            f'{first_line}Его роль: {role}.'
            f'Его токен: {token}\n'
            f'Его confirmation_code для обновления токена:\n'
            f'{confirmation_code}'
        )
        logger.debug(f'user_if_staff:{user.is_staff}')
        return user


class CustomUser(AbstractUser):
    """Кастомная модель пользователя."""
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        choices=ROLE_CHOICES,
        default='user',
        max_length=16
    )
    email = models.EmailField('E-MAIL', unique=True, blank=False, null=False)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=(
            RegexValidator(
                regex=r'^[mM][eE]$',
                message=(
                    'Попытка регистрации пользователя '
                    'под me-образным именем'
                ),
                inverse_match=True
            ),
        ),
    )

    objects = CustomUserManager()

    class Meta:
        ordering = ('-date_joined',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return f'{self.username}: {self.email}, уровень доступа: {self.role}'

    @property
    def token(self):
        token = AccessToken.for_user(self)
        token['role'] = self.role
        token['is_superuser'] = self.is_superuser
        return token

    @property
    def confirmation_code(self):
        dict = {
            'username': self.username,
            'email': self.email
        }
        confirmation_code = jwt.encode(
            dict,
            SECRET_KEY,
            'HS256'
        )
        return confirmation_code


class Category(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='url-адрес категории',
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Название жанра'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='url-адрес жанра',
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название произведения'
    )
    year = models.PositiveIntegerField(
        verbose_name='Год создания',
        default=0,
        db_index=True,
        validators=(validate_year,),
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        blank=True,
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=True,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведения',
        null=True
    )
    text = models.TextField(
        max_length=200,
        verbose_name='Текст отзыва'
    )
    score = models.IntegerField(
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)),
        error_messages={'validators': 'Укажите оценку от 1 до 10'},
        verbose_name='Оценка',
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
        null=True
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        # Данная команда не даст повторно голосовать
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique_review'
            )]

    def __str__(self):
        return text_processor(self.text, 1)


class Comment(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, null=True,
        related_name='comments', verbose_name='Произведение'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
        null=True
    )
    text = models.TextField('Текст комментария', max_length=200)
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, null=True
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return text_processor(self.text, 1)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from api_yamdb.settings import EMPTY_VALUE
from api.serializers import logger
from .models import Category, Comment, Genre, Review, Title, CustomUser


@admin.register(CustomUser)
class UserAdminConfig(UserAdmin):
    default_site = 'api_yamdb.users.admin.AdminAreaSite'
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role',
        'is_active',
        'date_joined'
    )
    search_fields = ('username', 'email')
    list_filter = ('is_superuser', 'is_staff')
    fieldsets = (
        ('Key fields', {
            'fields': ('username', 'email', 'password', 'role')
        }),
        ('Personal info', {
            'fields': (
                'first_name', 'last_name', 'bio'
            ), 'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff',),
        }),
        ('Date joined', {
            'fields': ('date_joined',)
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('extrapretty',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )

    def has_module_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        if obj:
            return request.user.is_staff and not obj.is_staff
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        logger.debug(obj)
        if obj:
            return request.user.is_staff and not obj.is_staff
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def save_model(self, request, obj, form, change):
        logger.debug(change)
        if isinstance(obj, CustomUser):
            logger.debug('The object was recognized as CustomUser instance')
            super().save_model(request, obj, form, change)
            user_role = obj.role
            username = obj.username
            if user_role == 'admin':
                obj.is_staff = True
            # на случай изменения объекта
            else:
                obj.is_staff = False
            obj.save()
            confirmation_code = obj.confirmation_code
            token = obj.token
            if change:
                if obj.is_superuser:
                    pre_first_line = (f'\tВНИМАНИЕ! Объект был изменен на '
                                      f'"суперпользователь {username}".')
                else:
                    pre_first_line = (f'\tВНИМАНИЕ! Объект был изменен на '
                                      f'"пользователь {username}".')
                first_line = (f'{pre_first_line}\n\tДля него были '
                              'созданы новые коды доступа.')
            else:
                if obj.is_superuser:
                    first_line = f'Создан суперпользователь {username}.'
                else:
                    first_line = f'Создан пользователь {username}.'
            # при запуске в производство поставить отправку по почте
            logger.debug(
                f'{first_line}\nЕго роль: {user_role}.\n'
                f'Его токен: {token}\n'
                f'Его confirmation_code для обновления токена:\n'
                f'{confirmation_code}'
            )
            logger.debug(f'user is active: {obj.is_active}')
            logger.debug(f'user is staff: {obj.is_staff}')
        else:
            super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdminConfig(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'review',
        'text',
        'pub_date'
    )
    empty_value_display = EMPTY_VALUE


@admin.register(Review)
class ReviewAdminConfig(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'score',
        'author',
        'pub_date'
    )
    empty_value_display = EMPTY_VALUE


@admin.register(Category)
class CategoryAdminConfig(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )


@admin.register(Genre)
class GenreAdminConfig(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    )


@admin.register(Title)
class TitleAdminConfig(admin.ModelAdmin):
    list_display = (
        'name',
        'year',
        'description',
        'category',
    )

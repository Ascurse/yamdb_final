import logging
import sys

from rest_framework.permissions import SAFE_METHODS, BasePermission

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(message)s - строка %(lineno)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
handler.setFormatter(formatter)
logger.disabled = False
logger.debug('Логирование из permissions запущено')


def admin_or_superuser(request):
    request_user = request.user
    logger.debug(f'request_user: {request_user}')
    is_staff = False
    is_superuser = False
    role = False
    try:
        is_staff = request_user.is_staff
    except KeyError:
        pass
    try:
        is_superuser = request_user.is_superuser
    except KeyError:
        pass
    try:
        role = request_user.role
    except AttributeError:
        pass
    logger.debug(f'staff: {is_staff}, superuser: {is_superuser}, role: {role}')
    return (is_staff or is_superuser or role == 'admin')


class IsAdminUserCustom(BasePermission):
    def has_permission(self, request, view):
        logger.debug(f'dir request: {dir(request)}')
        logger.debug('IsAdminUserCustomPermission запущен, уровень запроса.')
        logger.debug(f'admin_or_superuser: {admin_or_superuser(request)}')
        return admin_or_superuser(request)

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or admin_or_superuser(request))


class IsAdminModeratorUserPermission(BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        request_user = request.user
        try:
            user_role = request_user.role
        except AttributeError:
            pass
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or admin_or_superuser(request)
            or user_role == 'moderator'
        )


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or admin_or_superuser(request)
        )

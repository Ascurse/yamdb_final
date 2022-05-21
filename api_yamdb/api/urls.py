from django.urls import include, path
from rest_framework import routers

from .routers import CustomRouter
from .views import (
    APISignupView,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    TokenView,
    UserViewSet,
)

router_v1_a = CustomRouter()
router_v1_a.register(r'users', UserViewSet)
router_v1_b = routers.DefaultRouter()
router_v1_b.register(r'categories', CategoryViewSet, basename='categories')
router_v1_b.register(r'genres', GenreViewSet, basename='genres')
router_v1_b.register(r'titles', TitleViewSet, basename='titles')
router_v1_b.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                     basename='review')
router_v1_b.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)

urlpatterns = [
    path('v1/', include(router_v1_a.urls)),
    path('v1/auth/signup/', APISignupView.as_view()),
    path('v1/auth/token/', TokenView.as_view()),
    path('v1/', include(router_v1_b.urls)),
]

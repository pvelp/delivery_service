from django.urls import include, path
from rest_framework.routers import SimpleRouter

from users.apps import UsersConfig
from users.views import ActivateUserByGet, CustomUserViewSet

app_name = UsersConfig.name

users_router = SimpleRouter()

users_router.register("users", CustomUserViewSet, basename="users")

urlpatterns = [
    path('', include(users_router.urls)),
    path('users/activate/<str:uid>/<str:token>', ActivateUserByGet.as_view())
] + users_router.urls

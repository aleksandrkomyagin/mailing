from django.urls import include, path

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from .views import (ClientViewset, GetConfirmationCodeView, GetTokenView,
                    MailingViewset, UserViewSet)

v1_router = DefaultRouter()
v1_router.register('client', ClientViewset, basename='client')
v1_router.register('mailing', MailingViewset, basename='mailing')
v1_router.register('users', UserViewSet, basename='users')


app_name = 'api'

auth_urlpatterns = [
    path('signup/', GetConfirmationCodeView.as_view(), name='registration'),
    path('token/', GetTokenView.as_view(), name='token'),
]

urlpatterns = [
    path('', include(v1_router.urls), name='router_urls'),
    path('auth/', include(auth_urlpatterns), name='auth_urls'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'schema/docs/',
        SpectacularSwaggerView.as_view(url_name='api:schema'),
        name='docs'
    ),
]

from django.contrib import admin
from django.urls import path, include
from myapp.views import SendCodeAPIView, VerifyCodeAPIView, UserProfileAPIView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static


# Определение схемы OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="API для авторизации и профиля пользователя",
        default_version='v1',
        description="Документация API для авторизации, инвайт-кодов и работы с профилями пользователей.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@yourdomain.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path('send-code/', SendCodeAPIView.as_view(), name='send_code'),
    path('verify-code/', VerifyCodeAPIView.as_view(), name='verify_code'),
    path('profile/<str:phone_number>/', UserProfileAPIView.as_view(), name='user_profile'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # ReDoc UI
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

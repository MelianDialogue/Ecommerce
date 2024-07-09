from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('register/', views.register, name='register-url'),
    path('login/', views.user_login, name='login-url'),
    path('dashboard/', views.dashboard, name='home-url'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('accessibility/', views.accessibility, name='accessibility'),
    path('cookies/', views.cookies, name='cookies'),
    path('profile/', views.profile, name='profile-url'),
    path('contact/', views.contact, name='contact'),
    path('change_password/', views.change_password, name='change_password'),
    path('chatbot_view/', views.chatbot_view, name='chatbot_view'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('about/', views.about, name='about'),
    path('shipping/', views.shipping, name='shipping'),
    path('logout/', views.logout_view, name='logout-url'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
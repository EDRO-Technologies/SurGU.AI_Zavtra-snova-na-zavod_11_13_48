"""
URL configuration for backbotend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# backbotend/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

# Функция для корневого URL
# def home(request):
#     return HttpResponse("Welcome to the Django and Telegram bot project!")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.urls')),
    #path('', home, name='home'),  # Корневая страница
]

if settings.DEBUG:  # Только в режиме отладки
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


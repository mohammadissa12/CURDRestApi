from django.contrib import admin
from django.urls import path,include
from restapi_app import urls as restapi_urls
from rest_framework.authtoken import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('restapi/', include('restapi_app.urls')),
]
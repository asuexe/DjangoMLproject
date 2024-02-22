
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('',include('MLapp.urls')),
    path('',include('macromolecularapp.urls')),
    path("admin/", admin.site.urls),
]

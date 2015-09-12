from django.conf.urls import url, include

from . import views

urlpatterns = [
    url('', include('django.contrib.auth.urls')),
]


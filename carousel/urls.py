# carousel/urls.py
from django.urls import path
from .views import carousel_view

app_name = 'carousel'

urlpatterns = [
    path('', carousel_view, name='carousel'),
]

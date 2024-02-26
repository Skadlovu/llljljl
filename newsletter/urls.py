from django.urls import path
from .views import subscribe, subscribe_success, newsletter_list
app_name='newsletter'
urlpatterns = [
    path('newsletter/subscribe/', subscribe, name='subscribe'),
    path('newsletter/subscribe_success/', subscribe_success, name='subscribe_success'),
    path('newsletter/newsletter_list/', newsletter_list, name='newsletter_list'),
]

from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from profiles.views import register,profile
from django.contrib.auth import views as auth_views
from.views import about,contact


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),
    path('', include('newsletter.urls')),
    path('profile/', profile, name='profile'),
    path('register', register, name='register'),
    #path('login/', CustomLoginView.as_view(template_name='profiles/login.html'), name='login'),
    path('login', auth_views.LoginView.as_view (template_name='profiles/login.html'),name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='profiles/logout.html'),name='logout'),
    path('password_reset', auth_views.PasswordResetView.as_view(template_name='profiles/password_reset.html'), name='password_reset'),
    path('about/',about,name='about'),
    path('contact/',contact,name='contact'),
    path('',include('comment.urls'))
 ]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

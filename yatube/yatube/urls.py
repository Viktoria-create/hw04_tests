from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include(('users.urls', 'users'))),
    path('', include(('posts.urls', 'posts'), namespace='posts')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include(('about.urls', 'about'), namespace='about')),
]

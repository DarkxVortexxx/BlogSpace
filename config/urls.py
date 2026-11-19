from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),

    # Backend APIs
    path('api/accounts/', include('accounts.urls')),
    path('api/', include('blog.urls')),

    # Frontend homepage
    path('', serve, {
        'document_root': settings.BASE_DIR / 'frontend',
        'path': 'index.html'
    }),

    path('media/<path:path>', serve, {
        'document_root': settings.MEDIA_ROOT
    }),
    
    # Frontend CSS and JavaScript
    path('<path:path>', serve, {
        'document_root': settings.BASE_DIR / 'frontend'
    }),
]

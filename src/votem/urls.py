"""votem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from votem import settings

urlpatterns = [
    url(r'^api/admin/', admin.site.urls),
    url(r'^api/authe/', include('authe.urls', namespace='authe')),
    url(r'^api/polls/', include('polls.urls', namespace='polls')),
    url(r'^api/moderators/', include('moderators.urls', namespace='moderators')),
    url(r'^api/statistics/', include('statistics.urls', namespace='statistics')),
    # url(r'^api/push/', include('pushtoken.urls', namespace='pushtoken')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler500 = "moderators.views.handler500"
handler404 = "moderators.views.handler404"
handler400 = "moderators.views.handler400"

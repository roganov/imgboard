from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import TemplateView

from core.views import board_view, thread_view, markup_view


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'imgboard.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^__admin/', include(admin.site.urls)),

    url(r'api/markup/', markup_view, name='api-markup'),
    url(r'^about/markup/$', TemplateView.as_view(template_name='markup_syntax.html'), name='syntax'),
    url(r'^(?P<slug>\w+)/(?P<page>\d+/?)?$', board_view, name='board'),
    url(r'^(?P<slug>\w+)/t/(?P<thread_id>\d+)$', thread_view, name='thread'),
    url(r'^board/1/', TemplateView.as_view(template_name='thread.html')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
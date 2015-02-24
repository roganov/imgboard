from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

from core.views import BoardView, ThreadView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'imgboard.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^__admin/', include(admin.site.urls)),

    url(r'^(?P<slug>\w+)/(?P<page>\d+/?)?$', BoardView.as_view(), name='board'),
    url(r'^(?P<slug>\w+)/t/(?P<thread_id>\d+)$', ThreadView.as_view(), name='thread'),
    url(r'^board/1/', TemplateView.as_view(template_name='thread.html')),

)
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'imgboard.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^board/$', TemplateView.as_view(template_name='board.html')),
    url(r'^board/1/', TemplateView.as_view(template_name='thread.html')),

    url(r'^admin/', include(admin.site.urls)),
)
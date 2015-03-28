from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cr_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^', TemplateView.as_view(template_name="pages/index.html")),
    #url(r'^/about', TemplateView.as_view(template_name="pages/about.html"))
    #url(r'^/download', TemplateView.as_view(template_name="pages/download.html"))
)
from django.conf.urls import patterns, include, url
from django.contrib import admin
from cr_app import urls as api_urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cr_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(api_urls)),
)

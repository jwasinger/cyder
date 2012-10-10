from django.conf.urls.defaults import *
from django.views.decorators.csrf import csrf_exempt

from cyder.core.search.views import *

urlpatterns = patterns('',
                       url(r'^search_ajax', csrf_exempt(search_ajax),name='search-core-ajax'),
                       url(r'^$', csrf_exempt(search),name='search-core'),
                       )
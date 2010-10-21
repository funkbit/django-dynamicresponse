from django.conf.urls.defaults import *

urlpatterns = patterns('myblog.blog.views',
    url(r'^$', 'list_posts', name='list_posts'),
    url(r'^create/$', 'post', name='create_post'),
    url(r'^(?P<post_id>\d+)/$', 'post', name='post'),
    url(r'^(?P<post_id>\d+)/delete/$', 'delete_post', name='delete_post'),
)

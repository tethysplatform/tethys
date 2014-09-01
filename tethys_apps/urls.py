from django.conf.urls import patterns, url, include

from tethys_apps.django_utilties import generate_app_url_patterns

urlpatterns = patterns('',
    url(r'^$', 'tethys_apps.views.index', name='app_library'),
)

app_url_patterns = generate_app_url_patterns()

for namespace, urls in app_url_patterns.iteritems():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    urlpatterns.append(url(root_pattern, include(urls, namespace=namespace)))

print urlpatterns
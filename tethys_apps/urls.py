from django.conf.urls import patterns, url, include

from tethys_apps.utilities import generate_app_url_patterns

urlpatterns = patterns('',
    url(r'^$', 'tethys_apps.views.library', name='app_library'),
)

# Append the app urls urlpatterns
app_url_patterns = generate_app_url_patterns()

for namespace, urls in app_url_patterns.iteritems():
    root_pattern = r'^{0}/'.format(namespace.replace('_', '-'))
    urlpatterns.append(url(root_pattern, include(urls, namespace=namespace)))
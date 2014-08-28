import ckan.plugins as p
from ckan.lib.base import BaseController, h, abort
from ckan.lib.helpers import Page

from ckanext.tethys_apps.lib.app_harvester import SingletonAppHarvester

class AppsController(BaseController):
    
    def index(self):
        t = p.toolkit
        c = t.c
        _ = t._
        
        context = {'user': c.user or c.author}
         
        # Check permissions
        try:
            t.check_access('apps_read', context)
        except t.NotAuthorized:
            abort(401, _('Not authorized to see this page'))
                
        # Retrieve apps list from the harvester
        harvester = SingletonAppHarvester()
        app_list = sorted(harvester.apps, key=lambda app: app['name'])
        
        c.page = Page(
            collection=app_list,
            page=t.request.params.get('page', 1),
            url=h.pager_url,
            items_per_page=15
        )
        return t.render('apps_main/index.html')
        
        

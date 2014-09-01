from tethys_apps.base.app_base import AppBase


class MyFirstAppApp(AppBase):
    """
    Example implementation of an app (this is the initializer for the app)
    """
    def register_app(self, app):
        """
        Register the app
        """
        
        app.add_app(name='My First App',
                    index='my_first_app',
                    icon='my_first_app/images/icon.gif')

    def register_controllers(self, controllers):
        """
        Add controllers
        """
        root = 'my-first-app'

        controllers.add_controller(name='my_first_app',
                                   url='my-first-app',
                                   controller='my_first_app.controllers.index.index',
                                   root=root)

        controllers.add_controller(name='new_controller',
                                   url='my-first-app/new-controller',
                                   controller='my_first_app.controllers.new_controller.index',
                                   root=root)

        controllers.add_controller(name='new_controller_action',
                                   url='my-first-app/new-controller/{name}',
                                   controller='my_first_app.controllers.new_controller.hello',
                                   root=root)
                               
    def register_persistent_stores(self, persistent_stores):
        """
        Add one or more persistent stores
        """
        persistent_stores.add_persistent_store('stream_gage_db')
        persistent_stores.add_initialization_script('my_first_app.lib.init_stream_gages_db')


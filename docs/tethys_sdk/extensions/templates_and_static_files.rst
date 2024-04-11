**************************
Templates and Static Files
**************************

**Last Updated:** February 22, 2018

Templates and static files in extensions can be used in other apps.  The advantage to using templates and static files from extensions in your apps is that when you update the template or static file in the extension, all the apps that use them will automatically be updated. Just as with apps, store the templates in the ``templates`` directory and store the static files (css, js, images, etc.) in the ``public`` directory. When using an extension template in your app's controllers, import the extension and use it to render the templates.

For example, to use an extension template in one of your app's controllers:

::

    from tethysext.my_first_extension import Extension as MyFirstExtension

    def my_controller(request):
        """
        A controller in my app, not the extension.
        """
        ...
        return MyFirstExtension.render(request, 'a_template.html', context)

You can reference static files in your app's templates using the ``static`` tag, just as you would any other static resource. However, rather than using the ``public`` filter to namespace the file path for you, you will need to the use the namespaced path (i.e. include the extension package name):

.. code-block:: html

    {% load static %}

    <link href="{% static 'my_first_extension/css/a_css_file.css' %}" rel="stylesheet">
    <script src="{% static 'my_first_extension/js/a_js_file.css' %}" type="text/javascript"></script>
    <img src="{% static 'my_first_extension/images/an_image.png' %}">
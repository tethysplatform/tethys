**************************
Templates and Static Files
**************************

**Last Updated:** February 22, 2018

Templates and static files in extensions can be used in other apps.  The advantage to using templates and static files from extensions in your apps is that when you update the template or static file in the extension, all the apps that use them will automatically be updated. Just as with apps, store the templates in the ``templates`` directory and store the static files (css, js, images, etc.) in the ``public`` directory. Then reference the template or static file in your app's controllers and templates using the namespaced path.

For example, to use an extension template in one of your app's controllers:

::

    def my_controller(request):
        """
        A controller in my app, not the extension.
        """
        ...
        return render(request, 'my_first_extension/a_template.html', context)

You can reference static files in your app's templates using the ``static`` tag, just as you would any other static resource:

.. code-block:: html

    {% load static %}

    <link href="{% static 'my_first_extension/css/a_css_file.css' %}" rel="stylesheet">
    <script src="{% static 'my_first_extension/js/a_js_file.css' %}" type="text/javascript"></script>
    <img src="{% static 'my_first_extension/images/an_image.png' %}">
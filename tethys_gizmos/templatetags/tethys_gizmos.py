import os
import json
import time
from datetime import datetime
from django.conf import settings
from django import template
from django.template.loader import get_template
from django.template import TemplateSyntaxError
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.serializers.json import DjangoJSONEncoder

from ..gizmo_dependencies import global_dependencies

register = template.Library()

CSS_OUTPUT_TYPE = 'css'
JS_OUTPUT_TYPE = 'js'
CSS_EXTENSION = 'css'
JS_EXTENSION = 'js'
EXTERNAL_INDICATOR = '://'
VALID_OUTPUT_TYPES = (CSS_OUTPUT_TYPE, JS_OUTPUT_TYPE)


class HighchartsDateEncoder(DjangoJSONEncoder):
    """
    Special Json Encoder for Tethys
    """
    def default(self, obj):
        # Highcharts date serializer
        if isinstance(obj, datetime):
            return time.mktime(obj.timetuple()) * 1000
        return super(HighchartsDateEncoder, self).default(obj)


@register.filter(is_safe=True)
def isstring(value):
    """
    Filter that returns a type
    """
    if value is str:
        return True
    else:
        return False


@register.filter
def return_item(l, i):
    try:
        return l[i]
    except:
        return None


def json_date_handler(obj):
    if isinstance(obj, datetime):
        return time.mktime(obj.timetuple()) * 1000
    else:
        return obj


@register.filter
def jsonify(data):
    """
    Convert python data structures into a JSON string
    """
    return json.dumps(data, default=json_date_handler)

@register.filter
def divide(value, divisor):
    """
    Divide value by divisor
    """
    v = float(value)
    d = float(divisor)

    return v/d


class TethysGizmoIncludeNode(template.Node):
    """
    Custom template include node that returns Tethys gizmos
    """
    def __init__(self, gizmo_name, options, *args, **kwargs):
        super(TethysGizmoIncludeNode, self).__init__(*args, **kwargs)
        self.gizmo_name = gizmo_name
        self.options = template.Variable(options)

    def render(self, context):
        try:
            # Get the name of the gizmo to load
            gizmo_name = self.gizmo_name
            gizmo_templates_root = os.path.join('tethys_gizmos', 'gizmos')

            # Handle case where gizmo_name is a string literal
            if self.gizmo_name[0] in ('"', "'"):
                gizmo_name = self.gizmo_name.replace("'", '')
                gizmo_name = gizmo_name.replace('"', '')

            # Add gizmo name to 'gizmos_rendered' context variable (used to load static libraries
            if 'gizmos_rendered' not in context:
                context.update({'gizmos_rendered': []})

            if gizmo_name not in context['gizmos_rendered']:
                context['gizmos_rendered'].append(gizmo_name)

            # Determine path to gizmo template
            gizmo_file_name = '{0}.html'.format(gizmo_name)
            template_name = os.path.join(gizmo_templates_root, gizmo_file_name)

            # Retrieve the gizmo template and render
            t = get_template(template_name)
            c = context.new(self.options.resolve(context))
            return t.render(c)

        except:
            if settings.TEMPLATE_DEBUG:
                raise
            return ''


@register.tag
def gizmo(parser, token):
    """
    Similar to the include tag, gizmo loads special templates called gizmos that come with the django-tethys_gizmo
    app. Gizmos provide tools for developing user interface elements with minimal code. Examples include date pickers,
    maps, and interactive plots.

    To insert a gizmo, use the "gizmo" tag and give it the name of a gizmo and a dictionary of configuration parameters.

    Example::
        {% load tethys_gizmos %}

        {% gizmo example_gizmo options %}
        {% gizmo "example_gizmo" options %}

    NOTE: the "options" dictionary must be a template context variable.
    ALSO NOTE: All supporting css and javascript libraries are loaded using the gizmo_dependency tag (see below).
    """
    try:
        tag_name, gizmo_name, options_literal = token.split_contents()

    except ValueError:
        raise template.TemplateSyntaxError('"%s" tag requires exactly two arguments' % token.contents.split()[0])

    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError('"{0}" tag takes at least one argument: the name of the '
                                  'template to be included.'.format(bits[0]))

    return TethysGizmoIncludeNode(gizmo_name, options_literal)


class TethysGizmoDependenciesNode(template.Node):
    """
    Loads gizmo dependencies and renders in "script" or "link" tag appropriately.
    """

    def __init__(self, output_type, *args, **kwargs):
        super(TethysGizmoDependenciesNode, self).__init__(*args, **kwargs)
        self.output_type = output_type

    def render(self, context):
        # Get the gizmos rendered from the context
        gizmos_rendered = context['gizmos_rendered']

        # Compile list of unique gizmo dependencies
        dependencies = []

        # Add gizmo dependencies
        for rendered_gizmo in gizmos_rendered:
            try:
                # Retrieve the "gizmo_dependencies" module and find the appropriate function
                dependencies_module = __import__('tethys_gizmos.gizmo_dependencies', fromlist=[rendered_gizmo])
                dependencies_function = getattr(dependencies_module, rendered_gizmo)

                # Retrieve a list of dependencies for the gizmo
                gizmo_deps = dependencies_function(context)

                # Only append dependencies if they do not already exist
                for dependency in gizmo_deps:
                    if EXTERNAL_INDICATOR in dependency:
                        static_url = dependency
                    else:
                        static_url = static(dependency)

                    if static_url not in dependencies:
                        # Lookup the static url given the path
                        dependencies.append(static_url)

            except AttributeError:
                # Skip those that do not have dependencies
                pass

        # Add the global dependencies last
        for dependency in global_dependencies(context):
            if EXTERNAL_INDICATOR in dependency:
                static_url = dependency
            else:
                static_url = static(dependency)

            if static_url not in dependencies:
                # Lookup the static url given the path
                dependencies.append(static_url)

        # Create markup tags
        script_tags = []
        style_tags = []
        for dependency in dependencies:
            # Only process Script tags if the dependency has a ".js" extension and the output type is JS or not specified
            if JS_EXTENSION in dependency and (self.output_type == JS_OUTPUT_TYPE or self.output_type is None):
                script_tags.append('<script src="{0}" type="text/javascript"></script>'.format(dependency))

            # Only process Style tags if the dependency has a ".css" extension and the output type is CSS or not specified
            elif CSS_EXTENSION in dependency and (self.output_type == CSS_OUTPUT_TYPE or self.output_type is None):
                style_tags.append('<link href="{0}" rel="stylesheet" />'.format(dependency))

        # Combine all tags
        tags = style_tags + script_tags
        tags_string = '\n'.join(tags)
        return tags_string


@register.tag
def gizmo_dependencies(parser, token):
    """
    Load all gizmo dependencies (JavaScript and CSS).

    Example::

        {% gizmo_dependencies css %}
        {% gizmo_dependencies js %}
    """
    output_type = None

    bits = token.split_contents()
    if len(bits) > 2:
        raise TemplateSyntaxError('"{0}" takes at most one argument: the type of dependencies to output '
                                  '(either "js" or "css")'.format(token.split_contents()[0]))

    elif len(bits) == 2:
        output_type = bits[1]

    # Validate output_type
    if output_type:
        # Remove quotes
        if output_type[0] in ('"', "'"):
            output_type = output_type.replace("'", '')
            output_type = output_type.replace('"', '')

        # Lowercase
        output_type = output_type.lower()

        # Check for valid values
        if output_type not in VALID_OUTPUT_TYPES:
            raise TemplateSyntaxError('Invalid output type specified: only "js" and "css" are '
                                      'allowed, "{0}" given.'.format(output_type))

    return TethysGizmoDependenciesNode(output_type)

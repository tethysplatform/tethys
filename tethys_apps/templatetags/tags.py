from django import template
import re

register = template.Library()


def parse_tags(app_tags):
    """
    Parse given tags value, standardize, and remove duplicates.
    """
    app_tags = [_f for _f in re.split("[,]+ *", app_tags) if _f]
    tags = []

    for tag in app_tags:
        tag = tag.replace('"', '')
        tag = tag.replace("'", '')
        tag = re.sub(r"\s+", '-', tag)
        tag = tag.lower()
        tags.append(tag)

    tags = list(set(tags))
    return tags


@register.filter
def get_tags_from_apps(apps):
    tags_list = set([])

    if len(apps.get('configured', [])) > 5:
        for app in apps.get('configured'):
            if isinstance(app, dict):
                if not app.get('enabled', True) or not app.get('show_in_apps_library', True):
                    continue
                app_tags = app['tags']
            else:
                if not app.enabled or not app.show_in_apps_library:
                    continue
                app_tags = app.tags

            # Standardize tags and remove duplicates
            tags = parse_tags(app_tags)

            tag_tuples = []
            for tag in tags:
                # Create human readable version of tag for search field
                human_tag = tag.replace('-', ' ')
                human_tag = human_tag.title()
                # Create tuple pairs with tag and human readable version
                tag_tuples.append((tag, human_tag))

            tags_list.update(tag_tuples)

    return list(tags_list)


@register.filter
def get_tag_class(app):
    if isinstance(app, dict):
        app_tags = app['tags']
    else:
        app_tags = app.tags

    # Standardize tags and remove duplicates
    tags = parse_tags(app_tags)

    # Join tags into a single space delimited string
    tags_list = ' '.join(tags)
    return tags_list

from django import template
import re

register = template.Library()
#Generating a list of all available tags. This list then used to generate the filters/buttons in the app library page.
@register.filter
def get_tags_from_apps(apps):
    tags_list = []
    for app in apps:
        tags = app.tags
        tags = filter(None, re.split("[,]+",tags))
        for tag in tags:
            tag = re.sub(r"\s+", '', tag)
            tags_list.append(tag)
            tags_list = list(set(tags_list))
    return tags_list

@register.filter
def get_class(app):
    get_tags = app.tags
    get_tags = filter(None, re.split("[,]+", get_tags))
    tags = []
    for tag in get_tags:
        tag = re.sub(r"\s+",'',tag)
        tags.append(tag)

    tags_list = ' '.join(tags)
    # for tag in tags:
    #         tags_list.append(tag)
        # tags = filter(None, re.split("[,]+",tags))
        # app_tags = []
        # for tag in tags:
        #     app_tags.append(tag)
    return tags_list

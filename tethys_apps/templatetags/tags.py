from django import template
import re

register = template.Library()

@register.filter
def get_tags_from_apps(apps):
    tags_list = []
    apps_list =[]
    for app in apps:
        apps_list.append(app)

    if len(apps_list) > 5:
        for app in apps:
            tags = app.tags
            tags = filter(None, re.split("[,]+",tags))
            for tag in tags:
                tag = re.sub(r"\s+", '', tag)
                tags_list.append(tag)
                tags_list = list(set(tags_list))
        return tags_list

@register.filter
def get_tag_class(app):
    get_tags = app.tags
    get_tags = filter(None, re.split("[,]+", get_tags))
    tags = []
    for tag in get_tags:
        tag = re.sub(r"\s+",'',tag)
        tags.append(tag)

    tags_list = ' '.join(tags)

    return tags_list

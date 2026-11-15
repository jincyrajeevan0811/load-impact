from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """Return the current query string with the given keys replaced (used for pagination)."""
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ""):
            query.pop(key, None)
        else:
            query[key] = value
    return query.urlencode()


@register.filter
def get_item(mapping, key):
    try:
        return mapping.get(key, 0)
    except AttributeError:
        return 0

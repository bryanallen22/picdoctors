from string import Template

# Here are some examples you should use elsewhere:
# Python:
#     from common.emberurls import get_ember_url
#     get_ember_url('myname', param1='val1', param2='val2')
# Template:
#     {% load picdoctags %}
#     {% ember_url 'myname' param1='val1' param2='val2' %}

# Add a name for your url, and the string it resolves to (with parameters)
# Retrieve your url with a call to get_ember_url
ember_urls = {
        "album_markupview": "/home/#/albums/${album_id}/markupView",
        "album_markupedit": "/home/#/albums/${album_id}/markupEdit",
        "album_view":       "/home/#/albums/${album_id}/groups/${group_id}/pics/view",
        "account_settings": "/home/#/settings",
        "payments_settings": "/home/#/settings/payments",
}

def get_ember_url(name, **kwargs):
    """
    Returns an ember specific url

    Example:
        get_ember_url('name1', param1='val1', param2='val2') -- no params used
    """
    return Template( ember_urls[name] ).substitute( kwargs )


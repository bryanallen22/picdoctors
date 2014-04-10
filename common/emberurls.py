from string import Template

# Add a name for your url, and the string it resolves to (with parameters)
# Retrieve your url with a call to get_ember_url
ember_urls = {
        "album_markupview": "/home/#/albums/${album_id}/markupView",
        "album_view":       "/home/#/albums/${album_id}/groups/${group_id}/pics/view",
}

def get_ember_url(name, **kwargs):
    """
    Returns an ember specific url

    Example:
        get_ember_url('name1', param1='val1', param2='val2') -- no params used
    """
    return Template( ember_urls[name] ).substitute( kwargs )


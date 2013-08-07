import requests
import simplejson

# DigitalOcean client id and key
DO_SECRET_CLIENT_ID = 'rvAIA5RPF4O2xY2H3WbmQ'
DO_SECRET_API_KEY = 'IeCnpBf5f1VprFGwvWqHfwcjN5ofu5sBuzb1znDOq'

def get_client_n_key():
    return {
            'client_id' : DO_SECRET_CLIENT_ID,
            'api_key'   : DO_SECRET_API_KEY,
           }

def handle_url(url, params=None):
    """
    Take url/params, return JSON. Adds client/key for you.
    """
    if params is None:
        params = get_client_n_key()
    else:
        params.update( get_client_n_key() )
    url = 'https://api.digitalocean.com' + url
    request = requests.get(url, params=params)
    ret = simplejson.loads(request.text)
    if ret['status'] != 'OK':
        print "ERROR: ", ret['error_message']
        print "  requested url was: ", req.url
    request.raise_for_status() # Just to double check
    return ret

def get_size_id(name):
    """
    Get size by name
    """
    sizes = handle_url('/sizes')['sizes']
    for size in sizes:
        if size['name'] == name:
            return size['id']
    return None

def get_size_name(size_id):
    """
    Get name by size_id
    """
    sizes = handle_url('/sizes')['sizes']
    for size in sizes:
        if size['id'] == size_id:
            return size['name']
    return None

def get_droplets():
    """
    Get a list of all droplets
    """
    data = handle_url('/droplets/')
    return data['droplets']

def match_ssh_key(key_name):
    """
    Fetch ssh keys dynamically, return id of the one that matches key_name
    """
    keys = handle_url('/ssh_keys')['ssh_keys']
    for key in keys:
        if key['name'] == key_name:
            return key['id']
    return None

def get_droplet_id( name ):
    return 0

def create_droplet( name, size_name, image_id, region_id, key_name ):
    """
    Create a new droplet. Return it's id
    """
    ssh_key_id = match_ssh_key(key_name)
    size_id = get_size_id(size_name)
    params = {
        'name'       : name,
        'size_id'    : size_id,
        'image_id'   : image_id,
        'region_id'  : region_id,
        'ssh_key_id' : ssh_key_id,
    }
    droplet = handle_url('/droplets/new', params)['droplet']
    return droplet['id']

def destroy_droplet( name ):
    """
    Take a droplet down
    """
    id = get_droplet_id( name )
    status = handle_url( '/droplet/%d/destroy' % id )

def droplet_info(droplet_id):
    droplet = handle_url('/droplets/%d' % droplet_id)['droplet']
    asdfasdfsadfasdf

if __name__=="__main__":
    params = get_client_n_key()
    import ipdb; ipdb.set_trace()


def get_profile_or_None(request):
    """ Get the request user profile if they are logged in """
    if request.user.is_authenticated():
        return request.user.get_profile()
    return None
    

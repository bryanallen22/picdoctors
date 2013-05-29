# Create your views here.

def get_progressbar_vars(request, url_name):
    """
    Get variables which will be passed to skaa_progressbar.html
    to render correctly
    """

    # Do we return want to show the login step in the progress bar?
    show_login = request.session.get('progressbar_show_login', True)
    arrowclass = "arrow_signin" if show_login else "arrow_nosignin"

    # defaults
    ret = {
        'show_login'        : show_login,
        'arrowclass'        : arrowclass,
        'upload_progress'   : 'filled', # Always going to be filled
        'markup_progress'   : 'empty',
        'signin_progress'   : 'empty',
        'setprice_progress' : 'empty',
    }

    if url_name == 'upload':
        if request.user.is_authenticated():
            request.session['progressbar_show_login'] = False
        else:
            request.session['progressbar_show_login'] = True
    elif url_name == 'markup':
        ret['markup_progress']   = 'filled'
    elif url_name == 'signin':
        ret['markup_progress']   = 'filled'
        ret['signin_progress']   = 'filled'
    elif url_name == 'set_price':
        ret['markup_progress']   = 'filled'
        ret['signin_progress']   = 'filled'
        ret['setprice_progress'] = 'filled'
    else:
        ret = { }
    return ret

def show_progressbar_on_login_page(request):
    """
    Should we even show the progressbar on the sign in page at all?
    """
    return request.session.get('progressbar_show_login', False)

def clear_progressbar_cookie(request):
    if 'progressbar_show_login' in request.session:
        del request.session['progressbar_show_login']


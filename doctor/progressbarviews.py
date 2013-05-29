# Create your views here.

def get_doc_progressbar_vars(request):
    """
    Get variables which will be passed to doc_progressbar.html
    to render correctly
    """

    # defaults
    ret = {
        'show_progressbar'       : True,
        'arrowclass'             : 'arrow_doc',
        'merchant_info_progress' : 'empty',
        'bank_transfer_progress' : 'empty',
        'doc_profile_progress'   : 'empty',
        'remaining'              : 3,
    }

    complete = 0
    if request.user.is_merchant:
        ret['merchant_info_progress'] = 'filled'
        complete += 1
    if request.user.has_bank_account:
        ret['bank_transfer_progress'] = 'filled'
        complete += 1
    if request.user.pic or request.user.doc_profile_desc:
        ret['doc_profile_progress'] = 'filled'
        complete += 1

    if complete == 3:
        ret['show_progressbar'] = False

    ret['remaining'] = 3 - complete

    return ret


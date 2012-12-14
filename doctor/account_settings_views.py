# Create your views here.
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to

import settings

@login_required
def create_bank_account(request):
    profile = get_profile_or_None(request)
    if not profile or not profile.is_doctor:
        return HttpResponse('{ }', mimetype='application/json')
    
    if profile.bp_account_wrapper:
        raise KeyError("Can't create a new account for %s - he/she already has" \
                       " bp_account_wrapper.id=%s" % request.user.email, profile.bp_account_wrapper.id)

    try:
        account = balanced.Marketplace.my_marketplace.create_merchant(email_address, 
                              bank_account_uri=request.POST['bank_account_uri'])
        wrapper = BPAccountWrapper(uri=account.uri)
        wrapper.save()
        profile.bp_account_wrapper = wrapper
        profile.save()
    except balanced.exc.HTTPError as ex:
        if ex.category_code == 'duplicate-email-address':
            raise KeyError("Duplicate email address %s... this should have been saved under " \
                           "profile.bp_account_wrapper..." % email_address)
        else:
            raise

    # TODO add bank stuff here
    ret = {}
    response_data = simplejson.dumps(ret)
    return HttpResponse(response_data, mimetype='application/json')


@login_required
@render_to('account_settings_doc.html')
def settings_doc(request):
    return { 
        'marketplace_uri'   : settings.BALANCED_MARKETPLACE_URI,
    }


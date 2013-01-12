# Create your views here.
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.http import HttpResponse

from annoying.decorators import render_to

from common.functions import get_profile_or_None
from common.models import BPAccountWrapper

import balanced
import settings

@login_required
def create_bank_account(request):
    profile = get_profile_or_None(request)
    email_address = request.user.email
    if not profile or not profile.is_doctor:
        return HttpResponse('{ }', mimetype='application/json')

    try:

        # Configure balanced
        balanced.configure(settings.BALANCED_API_KEY_SECRET)
        
        # Get their account if they have one
        if profile.bp_account_wrapper:
            account = balanced.Account.find(profile.bp_account_wrapper.uri)
        else:
            # Create a new account and associate it with this profile
            account = balanced.Account().save()
            wrapper = BPAccountWrapper(uri=account.uri)
            wrapper.save()
            profile.bp_account_wrapper = wrapper
            profile.save()

        # Add the bank account to the user's account
        account.add_bank_account(request.POST['bank_account_uri'])

    except balanced.exc.HTTPError as ex:
        if ex.category_code == 'duplicate-email-address':
            raise KeyError("Duplicate email address %s... this should have been saved under " \
                           "profile.bp_account_wrapper..." % email_address)
        else:
            raise

    # TODO add bank stuff here
    ret = { "success" : True }
    response_data = simplejson.dumps(ret)
    return HttpResponse(response_data, mimetype='application/json')


@login_required
@render_to('account_settings_doc.html')
def settings_doc(request):
    profile = get_profile_or_None(request)
    balanced.configure(settings.BALANCED_API_KEY_SECRET)
    if profile.bp_account_wrapper:
        account = balanced.BankAccount.find(profile.bp_account_wrapper.uri)
        bank_accounts = [ba for ba in account.bank_accounts]
    else:
        bank_accounts = None

    return { 
        'marketplace_uri'   : settings.BALANCED_MARKETPLACE_URI,
        'bank_accounts'     : bank_accounts,
    }


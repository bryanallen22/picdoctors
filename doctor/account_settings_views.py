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
            account.email_address = email_address
            account.save()
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
def delete_bank_account(request):
    # TODO - don't delete the uri unless it's associated with
    # the logged in user. Just to be sure.

    profile = get_profile_or_None(request)
    if not profile or not profile.bp_account_wrapper:
        ret = { "success" : False }
    else:
        balanced.configure(settings.BALANCED_API_KEY_SECRET)

        account = balanced.Account.find(profile.bp_account_wrapper.uri)
        bank_accounts_uris = [ba.uri for ba in account.bank_accounts if ba.is_valid]
        delete_uri = request.POST['bank_account_uri']
        if delete_uri in bank_accounts_uris:
            bank_account = balanced.BankAccount.find(delete_uri)
            bank_account.delete()
            ret = { "success" : True }
        else:
            ret = { "success" : False }

    response_data = simplejson.dumps(ret)
    return HttpResponse(response_data, mimetype='application/json')

@login_required
@render_to('account_settings_doc.html')
def settings_doc(request):
    profile = get_profile_or_None(request)
    balanced.configure(settings.BALANCED_API_KEY_SECRET)
    if profile.bp_account_wrapper:
        account = balanced.BankAccount.find(profile.bp_account_wrapper.uri)
        bank_accounts = [ba for ba in account.bank_accounts if ba.is_valid]
    else:
        bank_accounts = None

    return { 
        'marketplace_uri'   : settings.BALANCED_MARKETPLACE_URI,
        'bank_accounts'     : bank_accounts,
    }

@login_required
def merchant_info(request):
    """
    POST should contain info to underwrite a doctor
    """
    profile = get_profile_or_None(request)
    balanced.configure(settings.BALANCED_API_KEY_SECRET)

    # Person
    merchant_data = {
        'type': 'person',

        'name': 'Timmy Q. CopyPasta',
        'street_address': '121 Skriptkid Row',
        'postal_code': '94110',
        'phone_number': '+14089999999',
        'dob': '1989-12',
    }
    
    # Business
    merchant_data = {
        'type': 'business',

        'name': 'Skripts4Kids',
        'street_address': '555 VoidMain Road',
        'postal_code': '91111',
        'phone_number': '+140899188155',
        'tax_id': '211111111',

        'person': {
            'name': 'Timmy Q. CopyPasta',
            'street_address': '121 Skriptkid Row',
            'postal_code': '94110',
            'phone_number': '+14089999999',
            'dob': '1989-12',
        },
    }

    account = balanced.Account().save()

    try:
        account.add_merchant(merchant_data)
    except balanced.exc.MoreInformationRequiredError as ex:
        # could not identify this account.
        logging.info('redirect merchant to:', ex.redirect_uri)
    except balanced.exc.HTTPError as error:
        # TODO: handle 400 and 409 exceptions as required
        raise


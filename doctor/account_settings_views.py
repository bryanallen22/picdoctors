# Create your views here.
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from annoying.decorators import render_to

from common.functions import get_profile_or_None
from common.balancedfunctions import get_merchant_account, is_merchant

import balanced
import settings
import logging

@login_required
def create_bank_account(request):
    profile = get_profile_or_None(request)
    
    if not profile or not profile.isa('doctor'):
        return HttpResponse('{ }', mimetype='application/json')

    account = get_merchant_account(request, profile)

    # Add the bank account to the user's account
    account.add_bank_account(request.POST['bank_account_uri'])

    # TODO add bank stuff here
    ret = { "success" : True }
    response_data = simplejson.dumps(ret)
    return HttpResponse(response_data, mimetype='application/json')

@login_required
def delete_bank_account(request):
    # TODO - don't delete the uri unless it's associated with
    # the logged in user. Just to be sure.

    profile = get_profile_or_None(request)
    if not profile or not profile.bp_account:
        ret = { "success" : False }
    else:
        balanced.configure(settings.BALANCED_API_KEY_SECRET)

        account = profile.bp_account.fetch()
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
def merchant_info(request):
    """
    POST should contain info to underwrite a doctor
    """
    profile = get_profile_or_None(request)
    balanced.configure(settings.BALANCED_API_KEY_SECRET)

    # used for both 'person' and 'business'
    if request.POST['merchant_type'] == 'person':
        merchant_data = {
            'type'           : request.POST['merchant_type'],
            'name'           : request.POST['name'],
            'street_address' : request.POST['street_address'],
            'postal_code'    : request.POST['postal_code'],
            'phone_number'   : request.POST['phone_number'],
            'dob'            : request.POST['birth_year'] + '-' + request.POST['birth_month'],
        }
    elif request.POST['merchant_type'] == 'business':
        merchant_data = {
            'type' : request.POST['merchant_type'],

            # business things
            'name'           : request.POST['business_name'],
            'street_address' : request.POST['business_street_address'],
            'postal_code'    : request.POST['business_postal_code'],
            'phone_number'   : request.POST['business_phone_number'],
            'tax_id'         : request.POST['business_tax_id'],

            # personal things
            'person' : {
                'name'           : request.POST['name'],
                'street_address' : request.POST['street_address'],
                'postal_code'    : request.POST['postal_code'],
                'phone_number'   : request.POST['phone_number'],
                'dob'            : request.POST['birth_year'] + '-' + required.POST['birth_month'],
            }
        }

    else:
        raise

    account = get_merchant_account(request, profile)

    try:
        account.add_merchant(merchant_data)
    except balanced.exc.MoreInformationRequiredError as ex:
        # could not identify this account.
        logging.info('redirect merchant to:', ex.redirect_uri)
        return redirect( ex.redirect_uri )
    except balanced.exc.HTTPError as error:
        # TODO: handle 400 and 409 exceptions as required
        raise

    # Bring them back to this page
    return redirect( reverse('account_settings') + '#merchant_tab' )

def get_settings_doc(request):
    profile = get_profile_or_None(request)
    if profile.bp_account:
        account = profile.bp_account.fetch()
        bank_accounts = [ba for ba in account.bank_accounts if ba.is_valid]
        merchant = is_merchant(account)
    else:
        bank_accounts = None
        merchant = False

    my_params = {
        'bank_accounts'     : bank_accounts,
        'is_merchant'       : merchant,
    }

    return my_params


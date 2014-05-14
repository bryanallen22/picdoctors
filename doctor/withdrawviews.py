# Create your views here.
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.humanize.templatetags.humanize import intcomma

from annoying.decorators import render_to

from common.models import *
from common.functions import get_profile_or_None
from common.balancedfunctions import get_merchant_account, get_withdraw_jobs, is_merchant, credit_doctor
from common.decorators import require_login_as

from collections import namedtuple

import balanced
import settings

#register = template.Library()

minimum_withdraw = 10.00

WithdrawRow = namedtuple('WithdrawRow', 'album_url, album_img_url, date, doc_earnings')

def generate_withdraw_rows(withdraw_jobs):
    """
    Generate rows for the withdraw page
    """
    ret = []
    for wj in withdraw_jobs:
        # Use the first pic of the job as thumbnail
        pics = Pic.objects.filter(album=wj.album, group__sequence__exact=1)

        # I'm going to assume I find at least 1
        pic_url = pics[0].get_thumb_url()

        ret.append( WithdrawRow(
            album_url=reverse('markup_album', args=[wj.album.id, 1]),
            album_img_url=pic_url,
            date=wj.created,
            doc_earnings=wj.payout_price_cents,
        ))

    return ret

@require_login_as(['doctor'])
@render_to('withdraw.html')
def withdraw(request):
    profile = get_profile_or_None(request)
    if request.method == "GET":
        account = get_merchant_account(request, profile)
        bank_accounts = [ba for ba in account.bank_accounts if ba.is_valid]

        if profile.isa('doctor') and len(bank_accounts) > 0 and is_merchant(account):
            valid = True
        else:
            valid = False

        withdraw_jobs = get_withdraw_jobs(profile)

        total = 0
        for job in withdraw_jobs:
            total += job.payout_price_cents

        rows = generate_withdraw_rows(withdraw_jobs)

        return {
            'valid'            : valid,
            'balance'          : float(total)/100,
            'minimum_withdraw' : minimum_withdraw,
            'rows'             : rows,
        }

    elif request.method == "POST":
        amount = credit_doctor(profile)
        return {
            'transfer_complete' : True,
            'amount'            : amount,
        }


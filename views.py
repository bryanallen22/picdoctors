from annoying.decorators import render_to
from django.template import RequestContext, loader
from django import http
import sys, traceback
import ipdb
import settings

@render_to('index.html')
def index(request):
    return locals()

def get_params():
    printout = ''
    if not settings.IS_PRODUCTION:
        printout = error()

    sys.exc_clear()

    return { 
            'printout': printout,
            }
        

#@render_to('500.html')
def oh_sob_500(request):
    """
    500 error handler.

    Context: sys.exc_info() results
    """
    t = loader.get_template('500.html')
    params = get_params()
    return http.HttpResponseNotFound(t.render(RequestContext(request, params)))

#@render_to('404.html')
def wheres_waldo_404(request):
    def handler404(request):
            return details(request, '404-page-url')
    """
    404 error handler.

    Context: sys.exc_info() results
    """
    t = loader.get_template('404.html')
    params = get_params()
    return http.HttpResponseNotFound(t.render(RequestContext(request, params)))


def error():
    tb =  traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
    return tb[len(tb)-1].replace('\n','')

def errorstack():
    return ''.join(traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))

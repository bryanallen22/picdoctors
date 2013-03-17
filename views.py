from annoying.decorators import render_to
from django.template import RequestContext, loader
from django import http
import sys, traceback
import ipdb

@render_to('index.html')
def index(request):
    return locals()

#@render_to('500.html')
def oh_sob_500(request):
    """
    500 error handler.

    Context: sys.exc_info() results
    """
    printout = error()
    sys.exc_clear()
    #return { 'printout' : printout }
    t = loader.get_template('500.html')
    return http.HttpResponseNotFound(t.render(RequestContext(request, {'request_path': request.path, 'printout': printout, })))

#@render_to('404.html')
def wheres_waldo_404(request):
    def handler404(request):
            return details(request, '404-page-url')
    """
    404 error handler.

    Context: sys.exc_info() results
    """
    printout = error()
    sys.exc_clear()
    t = loader.get_template('404.html')
    return http.HttpResponseNotFound(t.render(RequestContext(request, {'request_path': request.path, 'printout': printout, })))


def error():
    tb =  traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
    return tb[len(tb)-1].replace('\n','')

def errorstack():
    return ''.join(traceback.format_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2]))

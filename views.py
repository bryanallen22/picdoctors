from annoying.decorators import render_to

@render_to('index.html')
def index(request):
    return locals()

@render_to('500.html')
def error500(request):
    """
    500 error handler.

    Templates: `500.html`
    Context: sys.exc_info() results
    """
    ltype,lvalue,ltraceback = sys.exc_info()
    sys.exc_clear()
    return { 'type' : ltype, 'value' : lvalue, 'traceback' : ltraceback }

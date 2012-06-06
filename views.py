from annoying.decorators import render_to

@render_to('index.html')
def index(request):
    return locals()

@render_to('markup.html')
def markup(request):
    return locals()


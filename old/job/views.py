from annoying.decorators import render_to

@render_to('job.html')
def index(request):
    return locals()


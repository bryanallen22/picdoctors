from annoying.decorators import render_to


@render_to('doc_home.html')
def doc_home(request):
    return {}


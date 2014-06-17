# Create your views here.
from annoying.decorators import render_to

@render_to("photo-retouching.html")
def landing_general_retouching(request):
    return {}

@render_to("photo-restoration.html")
def landing_photo_restoration(request):
    return {}

@render_to("bridal-photo-retouching.html")
def landing_bridal_photo_retouching(request):
    return {}

@render_to("wedding-retouching.html")
def landing_wedding_retouching(request):
    return {}

@render_to("family-photo-retouching.html")
def landing_family_photo_retouching(request):
    return {}


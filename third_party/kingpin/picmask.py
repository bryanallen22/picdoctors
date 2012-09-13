import Image, ImageEnhance, ImageFont, ImageDraw

def reduceOpacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def addOverlayText(im, overlay_text):
    font = ImageFont.truetype("HelveticaNeueLight.ttf", 14)
    draw = ImageDraw.Draw(im)
    top = overlay_text[0]
    bottom = overlay_text[1]
    draw.text((10,10), top, (0,0,0), font=font)
    draw.text((10,im.size[1]-20), bottom, (0,0,0), font=font)

def watermark(im, mark, position, size, overlay_text, opacity):
    """Adds a watermark to an image."""
    mark = mark.resize(size)
    if opacity < 1:
        mark = reduceOpacity(mark, opacity)
    
    addOverlayText(mark, overlay_text)
    
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    layer.paste(mark, position)
    # composite the watermark with the layer
    return Image.composite(layer, im, layer)

def goCowGo():
    im = Image.open('cow.jpg')
    mark = Image.open('overlay.png')
    mask_width = int(im.size[0] * .39)
    mask_height = int(im.size[1] * .35)
    im_width = im.size[0]
    im_height = im.size[1]
    position = (im_width-mask_width, int(im_height/2))
    size = (mask_width, mask_height)
    text = ("Doctor: Santa Claus", "PicDoctors.com")
    opacity = 0.5
    watermark(im, mark, position, size, text, opacity).show()

goCowGo()

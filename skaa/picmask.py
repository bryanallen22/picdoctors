from PIL import Image, ImageEnhance, ImageFont, ImageDraw 

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

def addOverlayText(im, overlay_text, font):
    draw = ImageDraw.Draw(im)
    top = overlay_text[0]
    bottom = overlay_text[1]
    draw.text((10,10), top, (0,0,0), font=font)
    draw.text((10,im.size[1]-30), bottom, (0,0,0), font=font)

def watermark(im, mark, position, overlay_text, font, opacity):
    """Adds a watermark to an image."""
    if opacity < 1:
        mark = reduceOpacity(mark, opacity)
    
    addOverlayText(mark, overlay_text, font)
    
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    layer.paste(mark, position)
    # composite the watermark with the layer
    return Image.composite(layer, im, layer)

def generate_watermarked_image(im, specific_text):
    font = ImageFont.truetype("skaa/HelveticaNeueLight.ttf", 28)
    im_width = im.size[0]
    im_height = im.size[1]
    mask_width = int(im_width * .37)
    mask_height = int(im_height * .37)
    mask_size = (mask_width, mask_height)
    mark = Image.new('RGB', mask_size)
    draw = ImageDraw.Draw(mark) # Create a draw object
    draw.rectangle((0, 0, mask_width-1, mask_height-1), fill="black", outline="red")
    position = (im_width-mask_width, int(im_height/2))
    text = (specific_text, "PicDoctors.com")
    opacity = 0.5
    watermarked_image = watermark(im, mark, position, text, font, opacity)
#    watermarked_image.show()
    return watermarked_image

#im = Image.open('cow.jpg')
#generate_watermarked_image(im, 'Job #000000001')
#goMoo(im)

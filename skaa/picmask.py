from PIL import Image, ImageEnhance, ImageFont, ImageDraw 
import settings
import ipdb, os

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

def addOverlayText(im, overlay_text, font, font_size):
    colour = 'white'
    draw = ImageDraw.Draw(im)
    top = overlay_text[0]
    doc_handle = "  " + overlay_text[1] # use two spaces for indentation
    bottom = overlay_text[2]
    draw.text((font_size,font_size), top, colour, font=font)
    draw.text((font_size,int(2.5*font_size)), doc_handle, colour, font=font)
    draw.text((font_size,im.size[1]-font_size*2), bottom, colour, font=font)

def round_corner(radius, fill):
    """Draw a round corner"""
    corner = Image.new('RGBA', (radius, radius), (0, 0, 0, 0))
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner

def watermark(im, mark, position, overlay_text, font, font_size, opacity):
    """Adds a watermark to an image."""
    if opacity < 1:
        mark = reduceOpacity(mark, opacity)
    
    addOverlayText(mark, overlay_text, font, font_size)
    corner_radius = int(font_size / 2)
    corner = round_corner(corner_radius, "black")
    corner = reduceOpacity(corner, opacity)

    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    layer.paste(mark, position)
    layer.paste(corner, position)  # top left
    layer.paste(corner.rotate(90), # bottom left
                  (position[0],
                   position[1]+mark.size[1]-corner_radius))
    layer.paste(corner.rotate(270), # top right
                  (position[0]+mark.size[0]-corner_radius,
                   position[1]))
    layer.paste(corner.rotate(180),
                  (position[0]+mark.size[0]-corner_radius,
                   position[1]+mark.size[1]-corner_radius))
    # composite the watermark with the layer
    return Image.composite(layer, im, layer)

mask_ratio = .35  # 35% of image width
right_margin_ratio = 0.03 # 3% of image width

def generate_watermarked_image(im, doc_handle):
    im_width = im.size[0]
    im_height = im.size[1]
    mask_width = int(im_width * mask_ratio)
    mask_height = int(im_height * mask_ratio)
    mask_size = (mask_width, mask_height)
    right_margin = int(im_width * right_margin_ratio)
    mark = Image.new('RGB', mask_size)
    draw = ImageDraw.Draw(mark) # Create a draw object
    draw.rectangle((0, 0, mask_width-1, mask_height-1), fill="black")
    position = (im_width-mask_width-right_margin, int(im_height/2))
    text = ("Done by:", doc_handle, "www.PicDoctors.com")
    opacity = 0.5
    font_size = int(im_height * .035)
    font = ImageFont.truetype(
        os.path.join(settings.PROJECT_ROOT, "skaa/HelveticaBold.ttf"),
        font_size)
    watermarked_image = watermark(im, mark, position, text, font, font_size, opacity)
#    watermarked_image.show()
    return watermarked_image

#im = Image.open('cow.jpg')
#generate_watermarked_image(im, 'Job #000000001')
#goMoo(im)

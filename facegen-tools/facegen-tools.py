#!/usr/bin/env python
#
# GIMP-facegen-tools plugin, v1.1
#

from gimpfu import *
from array import array

def render_facegen(image, drawable, agemap, baselayer):
    gimp.context_push()
    image.undo_group_start()

    name = "facegen"
    type = RGBA_IMAGE
    opacity = 100
    result_layer = gimp.Layer(image, name,
                     baselayer.width, baselayer.height, type, opacity, NORMAL_MODE)
    result_layer.fill(FILL_TRANSPARENT)
    image.insert_layer(result_layer)

    width = baselayer.width
    height = baselayer.height
    baselayer_pr = baselayer.get_pixel_rgn(0, 0, width, height, False, False)
    base_pixels = array("B", baselayer_pr[0:width, 0:height])

    if (agemap.width != width or agemap.height != height):
        agemap.resize(width, height, 0, 0)
    agemap_pr = agemap.get_pixel_rgn(0, 0, width, height, False, False)
    agemap_pixels = array("B", agemap_pr[0:width, 0:height])

    result_pr = result_layer.get_pixel_rgn(0, 0, width, height, True, True)
    result_pixels = array("B", result_pr[0:width, 0:height])

    iterations = 0
    gimp.progress_init("Generating FaceGen Texture...")
    for y in range(0, height):
        for x in range(0, width):
            if (iterations % 100 == 0):
                progress = float(iterations) / float(width * height)
                gimp.progress_update(progress)
            iterations += 1

            new_pixels = result_pixels[(x+width*y)*4+0:(x+width*y)*4+4]

            fp_red = agemap_pixels[(x+width*y)*4+0] / 64.0
            fp_green = agemap_pixels[(x+width*y)*4+1] / 64.0
            fp_blue = agemap_pixels[(x+width*y)*4+2] / 64.0
            result_red = min( int(fp_red * base_pixels[(x+width*y)*4+0]), 255 )
            result_green = min( int(fp_green * base_pixels[(x+width*y)*4+1]), 255 )
            result_blue = min( int(fp_blue * base_pixels[(x+width*y)*4+2]), 255 )

            new_pixels[0], new_pixels[1], new_pixels[2], new_pixels[3] = result_red, result_green, result_blue, 255
            result_pixels[(x+width*y)*4+0:(x+width*y)*4+4] = new_pixels            

    result_pr[0:width, 0:height] = result_pixels.tostring()
    result_layer.flush()
    result_layer.merge_shadow(True)
    result_layer.update(0, 0, width, height)
    
    image.undo_group_end()
    gimp.context_pop()
    
    return

def calculate_agemap(image, drawable, facegen, baselayer):
    gimp.context_push()
    image.undo_group_start()

    name = "agemap"
    type = RGBA_IMAGE
    opacity = 100
    result_layer = gimp.Layer(image, name,
                     baselayer.width, baselayer.height, type, opacity, NORMAL_MODE)
    result_layer.fill(FILL_TRANSPARENT)
    image.insert_layer(result_layer)

    width = baselayer.width
    height = baselayer.height
    baselayer_pr = baselayer.get_pixel_rgn(0, 0, width, height, False, False)
    base_pixels = array("B", baselayer_pr[0:width, 0:height])

    facegen_pr = facegen.get_pixel_rgn(0, 0, width, height, False, False)
    facegen_pixels = array("B", facegen_pr[0:width, 0:height])

    result_pr = result_layer.get_pixel_rgn(0, 0, width, height, True, True)
    result_pixels = array("B", result_pr[0:width, 0:height])

    iterations = 0
    gimp.progress_init("Calculating Age Map...")
    for y in range(0, height):
        for x in range(0, width):
            if (iterations % 100 == 0):
                progress = float(iterations) / float(width * height)
                gimp.progress_update(progress)
            iterations += 1

            new_pixels = result_pixels[(x+width*y)*4+0:(x+width*y)*4+4]

            # base * (agemap/64) = facegen
            # agemap/64 = facegen / base
            # agemap = (facegen / base) * 64

            # clap minimum value at 5.0 (2% of 255) to decrease artifacts from extreme fraction values in agemap
            fp_red = max( float(base_pixels[(x+width*y)*4+0]), 5.0 )
            fp_green = max( float(base_pixels[(x+width*y)*4+1]), 5.0 )
            fp_blue = max( float(base_pixels[(x+width*y)*4+2]), 5.0 )
            fp_red = max( float(facegen_pixels[(x+width*y)*4+0]), 5.0) / fp_red * 64.0
            fp_green = max( float(facegen_pixels[(x+width*y)*4+1]), 5.0) / fp_green * 64.0
            fp_blue = max( float(facegen_pixels[(x+width*y)*4+2]), 5.0) / fp_blue * 64.0
            result_red = min( int(fp_red), 255 )
            result_green = min( int(fp_green), 255 )
            result_blue = min( int(fp_blue), 255 )
            
            new_pixels[0], new_pixels[1], new_pixels[2], new_pixels[3] = result_red, result_green, result_blue, 255
            result_pixels[(x+width*y)*4+0:(x+width*y)*4+4] = new_pixels            

    result_pr[0:width, 0:height] = result_pixels.tostring()
    result_layer.flush()
    result_layer.merge_shadow(True)
    result_layer.update(0, 0, width, height)
    
    image.undo_group_end()
    gimp.context_pop()

    return

register(
    "python-fu-render-facegen",
    "Render FaceGen Texture from Base Texture and Age Map ",
    "Render FaceGen Texture by multiplying Base Texture with (Age Map divided by 64). ",
    "public domain", "public domain", "2019",
    "Render FaceGen Texture...",
    "RGB*",
    [
        (PF_IMAGE, "image",       "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_LAYER, "agemap",      "Age Map", None),        
        (PF_LAYER, "baselayer",   "Base Layer", None),
    ],
    [],
    render_facegen,
    menu="<Image>/Filters/FaceGen Tools")

register(
    "python-fu-calculate-agemap",
    "Calculate Age Map from rendered face texture and base texture ",
    "Calculate Age Map from (rendered face texture divided by base texture) multiplied by 64. ",
    "public domain", "public domain", "2019",
    "Calculate Age Map...",
    "RGB*",
    [
        (PF_IMAGE, "image",       "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_LAYER, "facegen",     "Rendered Face", None),        
        (PF_LAYER, "baselayer",   "Base Layer", None),
    ],
    [],
    calculate_agemap,
    menu="<Image>/Filters/FaceGen Tools")


main()

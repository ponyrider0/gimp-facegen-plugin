#!/usr/bin/env python
#
# GIMP-facegen-tools plugin, v1.3
#

from gimpfu import *
from array import array
import os

def split_norm_and_spec(image, drawable, save_xcf):
    gimp.context_push()
    image.undo_group_start()

    if save_xcf:
        if image.filename is None:
            image.filename = "~/untitled"
        path, filename = os.path.split(image.filename)
        if "." not in filename or path == "~":
            path = os.path.expanduser('~')
            error_text = "Output path could not be determiend, saving to: " + path
            pdb.gimp_message(error_text)     
        filename_stem, notused_ext = os.path.splitext( filename )

    r_image, g_image, b_image, spec_image = pdb.plug_in_decompose(image, drawable, "RGBA", 0)
    normalmap_image = pdb.plug_in_compose(r_image, None, g_image, b_image, None, "RGB")

    gimp.delete(r_image)
    gimp.delete(g_image)
    gimp.delete(b_image)

    if save_xcf:
        norm_filename = filename_stem + "_norm.xcf"
        normalmap_image.filename = path + "/" + norm_filename
        pdb.gimp_file_save(normalmap_image, normalmap_image.layers[0], path + "/" + norm_filename, norm_filename)
        
        spec_filename = filename_stem + "_spec.xcf"
        spec_image.filename = path + "/" + spec_filename
        pdb.gimp_file_save(spec_image, spec_image.layers[0], path + "/" + spec_filename, spec_filename)

    gimp.Display(normalmap_image)
    gimp.Display(spec_image)
    gimp.displays_flush()

    image.undo_group_end()
    gimp.context_pop()
    
    return


def combine_norm_and_spec(image, drawable, normalmap, specmap, save_xcf, export_dds):
    gimp.context_push()
    image.undo_group_start()

    if save_xcf or export_dds: 
        if image.filename is None:
            image.filename = "~/untitled"
        path, filename = os.path.split(image.filename)
        if "." not in filename or path == "~":
            path = os.path.expanduser('~')
            error_text = "Output path could not be determiend, saving to: " + path
            pdb.gimp_message(error_text)
        filename_stem, notused_ext = os.path.splitext( filename )

    r_image, g_image, b_image, notused = pdb.plug_in_decompose(normalmap, drawable, "RGB", 0)
    combined_image = pdb.plug_in_compose(r_image, None, g_image, b_image, specmap, "RGBA")

    gimp.delete(r_image)
    gimp.delete(g_image)
    gimp.delete(b_image)
    gimp.delete(notused)

    if save_xcf:
        combined_image.filename = path + "/" + filename_stem + "_combiend.xcf"
        pdb.gimp_file_save(combined_image, combined_image.layers[0], path + "/" + filename_stem + "_combined.xcf", filename_stem + "_combined.xcf")

    if export_dds:
        pdb.file_dds_save(combined_image, combined_image.layers[0], #image, drawyable/layer
                          path + "/" + filename_stem + "_n.dds", filename_stem + "_n.dds", #filename, raw-filename
                          3, # compression: 0=none, 1=bc1/dxt1, 2=bc2/dxt3, 3=bc3/dxt5, 4=BC3n/dxt5nm, ... 8=alpha exponent... 
                          1, # mipmaps: 0=no mipmaps, 1=generate mipmaps, 2=use existing mipmaps(layers)
                          0, # savetype: 0=selected layer, 1=cube map, 2=volume map, 3=texture array
                          0, # format: 0=default, 1=R5G6B5, 2=RGBA4, 3=RGB5A1, 4=RGB10A2
                          -1, # transparent_index: -1 to disable (indexed images only)
                          0, # filter for generated mipmaps: 0=default, 1=nearest, 2=box, 3=triangle, 4=quadratic, 5=bspline, 6=mitchell, 7=lanczos, 8=kaiser
                          0, # wrap-mode for generated mipmaps: 0=default, 1=mirror, 2=repeat, 3=clamp
                          0, # gamma_correct: use gamma corrected mipmap filtering
                          0, # srgb: use sRGB colorspace for gamma correction
                          2.2, # gamma: gamma value used for gamma correction (ex: 2.2)
                          1, # perceptual_metric: use a perceptual error metric during compression
                          0, # preserve_alpha_coverage: preserve alpha test coverage for alpha channel maps
                          0) # alpha_test_threshold: alpha test threshold value for which alpha test coverage should be preserved    

    gimp.Display(combined_image)
    gimp.displays_flush()

    image.undo_group_end()
    gimp.context_pop()
    
    return

    

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
    "python-fu-combine-norm-and-spec",
    "Combine Norm and Spec Maps ",
    "Combine Norm and Spec Maps into RGBA-type normal map and save as new image. ",
    "public domain", "public domain", "2019",
    "Combine Norm and Spec Maps...",
    "RGB*",
    [
        (PF_IMAGE, "image",       "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_IMAGE, "normmap",     "Normal Map", None), 
        (PF_IMAGE, "specmap",     "Specular Map", None),
        (PF_TOGGLE, "save_xcf",   "Save XCF", False),
        (PF_TOGGLE, "export_dds", "Export DDS", False),
    ],
    [],
    combine_norm_and_spec,
    menu="<Image>/Filters/FaceGen Tools/Normals")

register(
    "python-fu-split-norm-and-spec",
    "Split Norm and Spec Maps from _n.dds file ",
    "Split Norm and Spec Maps from _n.dds file and save as new images. ",
    "public domain", "public domain", "2019",
    "Split Norm and Spec Maps from _N.DDS...",
    "RGBA",
    [
        (PF_IMAGE, "image",       "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_TOGGLE, "save_xcf",   "Save XCF", False),
    ],
    [],
    split_norm_and_spec,
    menu="<Image>/Filters/FaceGen Tools/Normals")

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

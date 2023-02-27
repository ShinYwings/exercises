import xml.etree.ElementTree as et
import xml.dom.minidom
import os
from glob import glob
import re
import numpy as np
import mitsuba

# Set the desired mitsuba variant
mitsuba.set_variant('scalar_rgb')

from mitsuba.core import Bitmap, Struct, Thread
from mitsuba.core.xml import load_file

def make_scene(*args):
    
    # Add the scene directory to the FileResolver's search path
    Thread.thread().file_resolver().append(os.path.dirname(args[2]))

    # Load the actual scene
    scene = load_file(args[2])

    # Call the scene's integrator to render the loaded scene
    scene.integrator().render(scene, scene.sensors()[0])
    
    # After rendering, the rendered data is stored in the film
    film = scene.sensors()[0].film()

    root = args[1]

    # Write out rendering as high dynamic range OpenEXR file
    film.set_destination_file(os.path.join(root, '{}.hdr'.format(args[0])))
    film.develop()

    # Write out a tonemapped JPG of the same rendering
    bmp = film.bitmap(raw=True)
    bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.UInt8, srgb_gamma=True).write(os.path.join(root, '{}.jpg'.format(args[0])))

    # Get linear pixel values as a numpy array for further processing
    bmp_linear_rgb = bmp.convert(Bitmap.PixelFormat.RGB, Struct.Type.Float32, srgb_gamma=False)
    image_np = np.array(bmp_linear_rgb)
    print(image_np.shape)

def make_xml():
    
    cwd = os.getcwd()

    bunny_path = os.path.join(cwd, "DataGeneration/rendering/bunny_003_0000_m000_0_000000.serialized")
    plane_path = os.path.join(cwd, "DataGeneration/rendering/Plane_003_0000_m000_0_000000.serialized")
    xml_filename = os.path.join(cwd, "DataGeneration/rendering/render.xml")

    # proc_list = ["train", "test"]
    proc_list = ["test"]

    for proc in proc_list:
        save_path = os.path.join(cwd, "DataGeneration/dataset/{}/render".format(proc))
        if not os.path.isdir(save_path):
            os.mkdir(save_path)
        
        dir_path = os.path.join(cwd, "DataGeneration/dataset/{}/hdr".format(proc))
        hdr_path = os.path.join(dir_path, "*.hdr")
        data_list = glob(hdr_path)
        data_list.sort()

        # For unit test        
        # save_path = os.path.join(cwd, "DataGeneration/dataset/train/")
        # dir_path = os.path.join(cwd, "DataGeneration/dataset/train/hdr")

        # with open("/home/shin/shinywings/research/sky_ldr2hdr/DataGeneration/rendering/imgs.txt", "r") as f:
        #     data_list = [line.rstrip() for line in f]
        # data_list.sort()

        for data in data_list:

            m = re.split(dir_path, data)[1]
            m = re.split(".hdr", m)[0]
            m = re.split("/", m)[1]
            
            scene = et.Element("scene", version = "2.2.1")

            integrator = et.SubElement(scene, "integrator", name="integrator", type = "direct")
            et.SubElement(integrator, "boolean", name = "hide_emitters", value = "false")

            sensor = et.SubElement(scene,"sensor", type = "perspective")
            et.SubElement(sensor,"float", name = "far_clip", value = "100.0")
            et.SubElement(sensor, "float", name = "focus_distance", value = "23.4563")
            et.SubElement(sensor, "float", name = "fov", value = "20.3117")
            et.SubElement(sensor,"string", name = "fov_axis", value = "x")
            et.SubElement(sensor, "float", name = "near_clip", value = "0.1")

            sensor_transform = et.SubElement(sensor, "transform", name = "to_world")
            et.SubElement(sensor_transform, "lookat", origin="11.4325, 21.8848, 1.72842", target="11.4672, 20.9288, 2.01965", up = "-0.00128896, -0.291446, -0.956587")
            sampler = et.SubElement(sensor, "sampler", type = "ldsampler")
            et.SubElement(sampler,"integer", name = "sample_count", value = "256")

            film = et.SubElement(sensor, "film", type = "hdrfilm")
            et.SubElement(film, "integer", name = "width", value = "64")
            et.SubElement(film, "integer", name = "height", value = "64")
            et.SubElement(film, "string", name = "pixel_format", value = "rgb")
            et.SubElement(film, "rfilter", type = "gaussian")

            obj_bsdf = et.SubElement(scene, "bsdf", id = "diffuse.003-bl_mat-bsdf", type = "diffuse")
            et.SubElement(obj_bsdf, "rgb", name = "reflectance", value = "0.288298, 0.288298, 0.288298")

            obj = et.SubElement(scene, "shape", id = "bunny.003_bunny.003_0000_m000_0.000000", type = "serialized")
            obj_transform = et.SubElement(obj, "transform", name = "to_world")
            et.SubElement(obj_transform, "matrix", value = "1.962585 0.000000 0.385044 12.443063 0.000000 2.000000 -0.000000 -5.115613 -0.385044 0.000000 1.962585 10.234327 0.000000 0.000000 0.000000 1.000000" )
            et.SubElement(obj, "ref", name = "bsdf", id = "diffuse.003-bl_mat-bsdf")
            et.SubElement(obj,"string", name = "filename", value = bunny_path)

            emitter = et.SubElement(scene,"emitter", type = "envmap")

            emitter_transform = et.SubElement(emitter, "transform", name = "to_world")
            et.SubElement(emitter_transform, "matrix", value = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1")
            et.SubElement(emitter_transform, "rotate", y="1", angle = "0")

            et.SubElement(emitter, "float", name = "scale", value = "1")
            et.SubElement(emitter,"string", name = "filename", value = data)

            plane_bsdf = et.SubElement(scene, "bsdf", id = "diffuse_ground.003-bl_mat-bsdf", type = "diffuse")
            et.SubElement(plane_bsdf, "rgb", name = "reflectance", value = "0.114435 0.097587 0.082283")

            plane = et.SubElement(scene, "shape", id = "Plane.003_Plane.003_0000_m000_0.000000", type = "serialized")
            plane_transform = et.SubElement(plane, "transform", name = "to_world")
            et.SubElement(plane_transform, "matrix", value = "7.000000 0.000000 0.000000 12.565207 0.000000 0.000000 11.000000 -6.645764 0.000000 -14.150000 0.000000 3.963688 0.000000 0.000000 0.000000 1.000000")

            et.SubElement(plane, "ref", name = "bsdf", id = "diffuse_ground.003-bl_mat-bsdf")
            et.SubElement(plane, "string", name = "filename", value = plane_path)

            rough_string = et.tostring(scene,"utf-8")
            reparsed = xml.dom.minidom.parseString(rough_string)

            reparsed_pretty = reparsed.toprettyxml(indent=""*4)

            with open(xml_filename,"w") as cube_xml:
                cube_xml.write(reparsed_pretty)

            make_scene(m, save_path, xml_filename)

            # subprocess.check_output(["python3", render_scene, m, save_path])
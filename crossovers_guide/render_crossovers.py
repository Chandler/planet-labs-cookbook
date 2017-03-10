import sys
import json
import zipfile
import urllib
import os
from PIL import Image
import requests
from StringIO import StringIO
from subprocess import call

input_path = sys.argv[1]
output_dir = sys.argv[2]

if not os.path.exists(output_dir):
  os.makedirs(output_dir)

def download_hyperion_browse(id, output_dir):
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)

  url = "https://earthexplorer.usgs.gov//browse/gisready/eo-1/hyp/{}".format(id)
  path = "{}/{}.zip".format(output_dir, id)
  print "downloading: {}".format(url)
  urllib.urlretrieve(url, path)
  zip_ref = zipfile.ZipFile(path, 'r')
  zip_ref.extractall(output_dir)
  zip_ref.close()

def download_planet_browse(
        item_type,
        item_id,
        api_key,
        width,
        output_dir):
  url = "https://tiles0.planet.com/v1/experimental/tiles/{}/{}/thumb?api_key={}&width={}".format(
        item_type, item_id, api_key, width)
  print "downloading: {}".format(url)
  response = requests.get(url)
  img = Image.open(StringIO(response.content))
  path = "{}/{}_{}.png".format(output_dir, item_type, item_id)
  img.save(path)
  return path

def build_worldfile(resolution, x, y, output_path):
    """
    http://www.gdal.org/frmt_various.html#WLD
    A world file file is a plain ASCII text file consisting of six values
    separated by newlines. The format is:

    pixel X size
    rotation about the Y axis (usually 0.0)
    rotation about the X axis (usually 0.0)
    negative pixel Y size
    X coordinate of upper left pixel center
    Y coordinate of upper left pixel center
    """
    with open(output_path, "w") as f:
        lines = [
            float(resolution),
            0.0,
            0.0,
            -float(resolution),
            float(x),
            float(y)]
        f.write("\n".join([str(l) for l in lines]))

def calculate_new_resolution(new_width, old_width, old_resolution):
    ratio = float(old_width)/float(new_width)
    new_resolution = float(old_resolution) * ratio
    print old_width, old_resolution, new_width, new_resolution
    return new_resolution


def merge_images(item_output_dir, hyperion_id, crossovers):
    hyperion_id = hyperion_id.split("_")[0]
    current_dir = os.getcwd()
    os.chdir(item_output_dir)
    cmds = []

    hyperion_tif = "/tmp/{}_transparent.tif".format(hyperion_id)
    hyperion_geo_tif = "/tmp/{}_geotiff.tif".format(hyperion_id)

    cmds.append("convert {}.jpg -transparent black {}".format(hyperion_id, hyperion_tif))
    cmds.append("geotifcp -e {}.wld {} {}".format(hyperion_id, hyperion_tif, hyperion_geo_tif))

    images = []
    images.append(hyperion_geo_tif)
    for crossover in crossovers:
        planet_id = crossover["id"]
        item_type = crossover["properties"]["item_type"]
        planet_tif = "/tmp/{}_transparent.tif".format(planet_id)
        planet_geo_tif = "/tmp/{}_geotiff.tif".format(planet_id)
        cmds.append("convert -trim {}_{}.png {}".format(item_type, planet_id, planet_tif))
        cmds.append("geotifcp -e {}_{}.wld {} {}".format(item_type, planet_id, planet_tif, planet_geo_tif))
        images.append(planet_geo_tif)

    cmds.append("rio merge {} --output {}".format(" ".join(images), "{}_merged.tiff".format(hyperion_id)))

    for cmd in cmds:
        print "running {}".format(cmd)
        call(cmd.split(" "))
    os.chdir(current_dir)

with open(input_path) as f:
    crossover_groups = json.loads(f.read())
    for crossover_group in crossover_groups:
        id = crossover_group["usgs_id"]
        item_output_dir = "{}/{}".format(output_dir, id)

        download_hyperion_browse(id, "{}/{}".format(output_dir, id))

        for crossover in crossover_group["crossovers"]:
            item_id = crossover["id"]
            item_type = crossover["properties"]["item_type"]

            download_planet_browse(
                item_type,
                item_id,
                os.environ["PLANET_API_KEY"],
                500,
                item_output_dir
            )

            path = "{}/{}_{}.png".format(item_output_dir, item_type, item_id)
            image = Image.open(path)
            width, height = image.size

            resolution = calculate_new_resolution(
                new_width=width,
                old_width=crossover["properties"]["columns"],
                old_resolution=crossover["properties"]["pixel_resolution"])
            x = crossover["properties"]["origin_x"]
            y = crossover["properties"]["origin_y"]

            build_worldfile(
                resolution,
                x,
                y,
                "{}/{}_{}.wld".format(item_output_dir, item_type, item_id))

        merge_images(item_output_dir, id, crossover_group["crossovers"])
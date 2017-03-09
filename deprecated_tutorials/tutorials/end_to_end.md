# End-to-End Search, Activation & Download

Sometimes you just want to download everything for an AOI. So given a query, how do you do it?

Let's start with the `redding_reservoir` query that we used in [part 1](intro_part_1_search.md). We've got it sitting in `redding.json`, but here it is in full:

```shell
> cat redding.json | jq
{
  "config": [
    {
      "field_name": "geometry",
      "config": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              -122.52227783203125,
              40.660847697284815
            ],
            [
              -122.52227783203125,
              40.987154933797335
            ],
            [
              -122.01690673828124,
              40.987154933797335
            ],
            [
              -122.01690673828124,
              40.660847697284815
            ],
            [
              -122.52227783203125,
              40.660847697284815
            ]
          ]
        ]
      },
      "type": "GeometryFilter"
    },
    {
      "field_name": "acquired",
      "config": {
        "gte": "2016-07-01T00:00:00.000Z",
        "lte": "2016-08-01T00:00:00.000Z"
      },
      "type": "DateRangeFilter"
    },
    {
      "field_name": "cloud_cover",
      "config": {
        "lte": 0.5
      },
      "type": "RangeFilter"
    }
  ],
  "type": "AndFilter"
}
```

Using the [download.py](download.py) script, which has a simple command line interface, we'll be able to go from searching for imagery, activating it, checking the status of activation, and downloading each file.

To start, let's look at the CLI using the `--help` flag:

```shell
python download.py --help
usage: download.py [-h] [--search] [--check] [--activate]
                   [--download DOWNLOAD]
                   query item asset

positional arguments:
  query                Path to json file containing query
  item                 Item type (e.g. REOrthoTile or PSOrthoTile
  asset                Asset type (e.g. visual, analytic, analytic_xml

optional arguments:
  -h, --help           show this help message and exit
  --search
  --check
  --activate
  --download DOWNLOAD  Path where downloaded files should be stored
```

So with that in mind, let's see what's available, using the `--search` flag:

```shell
> python download.py --search redding.json REOrthoTile visual
30 available images
```

Great! Let's see if they're activated, using the `--check` flag.

```shell
> $ python download.py --check redding.json REOrthoTile visual
20160707_195147_1057916_RapidEye-1: active
20160707_195146_1057917_RapidEye-1: active
20160707_195150_1057817_RapidEye-1: active
20160707_195143_1058017_RapidEye-1: inactive
20160707_195143_1058016_RapidEye-1: inactive
...
3 of 30 items are active
```

Ok, so at the time of writing only a few images are ready for download. Let's change that using the `--activate` flag.

```shell
> python download.py --activate redding.json REOrthoTile visual
Activating visual for 20160707_195147_1057916_RapidEye-1
Activation process started successfully
Activating visual for 20160707_195146_1057917_RapidEye-1
Activation process started successfully
Activating visual for 20160707_195150_1057817_RapidEye-1
Activation process started successfully
...
```

Cool! Now go grab some coffee - activation can happen in a couple of minutes, or can take 10s of minutes.

...  
...  
...  

Let's double-check that activation is complete using the `--check` flag:

```shell
> python download.py --check redding.json REOrthoTile visual
20160707_195147_1057916_RapidEye-1: active
20160707_195146_1057917_RapidEye-1: active
20160707_195150_1057817_RapidEye-1: active
20160707_195143_1058017_RapidEye-1: active
20160707_195143_1058016_RapidEye-1: active
20160707_195150_1057816_RapidEye-1: active
```

Sweet! Now we're ready to download some imagery! Use the `--download` flag, and supply a directory to download into (e.g. `/tmp`). You can add the `--overwrite` flag if you want to overwrite exsiting files, but the default is to skip existing files.

```shell
> python download.py --download /tmp redding.json REOrthoTile visual
File /tmp/20160707_195147_1057916_RapidEye-1_visual.tif exists - skipping ...
File /tmp/20160707_195146_1057917_RapidEye-1_visual.tif exists - skipping ...
Downloading 20160707_195150_1057817_RapidEye-1 to /tmp/20160707_195150_1057817_RapidEye-1.tif
Downloading 20160707_195143_1058017_RapidEye-1 to /tmp/20160707_195143_1058017_RapidEye-1.tif
Downloading 20160707_195143_1058016_RapidEye-1 to /tmp/20160707_195143_1058016_RapidEye-1.tif
```

And there you have it - some beautiful Rapideye imagery sitting on your hard drive. Have fun!

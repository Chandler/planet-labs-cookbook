# Planet Labs API v1 Walkthrough, Part 2

See [part 1](intro_part_1_search.md) for instructions on using this guide and acquiring a Planet Labs API key.

This tutorial will walk you through how to download your first image from the API. 

Downloading a large amount of imagery from our API can be tricky. So when you're done with this tutorial you may want to check this out: [Large AOI Best Practices](large_aoi_best_practices.md)

* [Accessing a Single Item](#single)
* [Asset Types](#types)
* [Asset Activation](#activate)
* [Asset Downloading](#download)


<a name="single"></a>
## Accessing a Single Item
In the last section, we learned how to search for items that interest us. 

Items are identified by their ItemType and ItemId. Here is one of the items from our part 1 search.

```
ItemType: REOrthoTile
ItemId: 20160707_195147_1057916_RapidEye-1
```

An easy way to visualize this item before we download it is to extract its footprint and view the geometry on geojson.io:

```sh
curl -L -H "Authorization: api-key $PLANET_API_KEY" \
    'https://api.planet.com/data/v1/item-types/REOrthoTile/items/20160707_195147_1057916_RapidEye-1' \
    | jq '.geometry' | geojsonio
```

<img src="../images/geojson3.png" style="width: 400px;"/>


<a name="types"></a>
## Asset Types

In general, a single satellite image can be provided in many different formats for different use cases. Some users want color-corrected products that can be viewed on the web, while others want raw image data for scientific purposes.

In the Planet API, these different item options are called Assets and items usually have multiple asset types.

We can see what asset types are availiable for a certain item by adding /assets to the item url.

```sh
curl -L -H "Authorization: api-key $PLANET_API_KEY" \
    'https://api.planet.com/data/v1/item-types/REOrthoTile/items/20160707_195147_1057916_RapidEye-1/assets' \
    | jq 'keys'
[
  "analytic",
  "analytic_xml",
  "udm",
  "visual",
  "visual_xml"
]
```

The `analytic` type is appropriate for scientific analysis (technically it's a radiance product, and also includes near-infrared data if available), while the types ending in `_xml` are XML metadata files for those who need it. `udm` is a `usable data mask` that tells you which pixels in an image are actually useful (cloudy pixels aren't, for example). A `visual` product includes red, green and blue bands, and has been color corrected for use in web mapping applications.

<a name="activate"></a>
## Asset Activation

An important thing to know about the API is that it does not pre-generate Assets, so they are not always immediately availiable to download. 

You can see that the visual asset for this item (at the time of writing) has the status "inactive". So we need to activate it.


```sh
curl -L -H "Authorization: api-key $PLANET_API_KEY" \
    'https://api.planet.com/data/v1/item-types/REOrthoTile/items/20160707_195147_1057916_RapidEye-1/assets/' \
    | jq .visual.status
"inactive"
```

Activation can sometimes take 10s of minutes to complete, so a common practice is to activate your desired items and then periodically check the status until it becomes "active".

In practice you will probably be activating many assets, but for now let's just activate one:

[examples/activation.py](../examples/activation.py)

```python
import os
import requests

item_id = "20160707_195147_1057916_RapidEye-1"
item_type = "REOrthoTile"
asset_type = "visual"

# setup auth
session = requests.Session()
session.auth = (os.environ['PLANET_API_KEY'], '')

# request an item
item = \
  session.get(
    ("https://api.planet.com/data/v1/item-types/" +
    "{}/items/{}/assets/").format(item_type, item_id))

# extract the activation url from the item for the desired asset
item_activation_url = item.json()[asset_type]["_links"]["activate"]

# request activation
response = session.post(item_activation_url)

print response.status_code

```

```sh
➜  python examples/activation.py
204 # HTTP 204: Success, No Content to show
```

<img src="../images/15_minutes_later.jpg" style="width: 400px;"/>


<a name="download"></a>
## Asset Downloading 

Let's check on our asset

```sh
curl -L -H "Authorization: api-key $PLANET_API_KEY" \
    'https://api.planet.com/data/v1/item-types/REOrthoTile/items/20160707_195147_1057916_RapidEye-1/assets/' \
    | jq .visual.status
"active" # perfect
```

Now that the visual asset is active, we can finally get to the good stuff, downloading the image. When an asset is active the direct link to download is present on the asset object in the "location" field:

```sh
➜  curl -L -H "Authorization: api-key $PLANET_API_KEY" \
'https://api.planet.com/data/v1/item-types/REOrthoTile/items/20160707_195147_1057916_RapidEye-1/assets/' \
| jq .visual.location

"https://api.planet.com/data/v1/download?token=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwUDNCNU9aYVFKUnN2WGsydmF3UVpLL2ZWci9DZWk0bG82OGJuT2NRR2laZ01EcFBTUnpsSWdHNGlZM2R5YTZWQ2xHdDROeFBka29Kb295a1BvdktPUT09IiwiaXRlbV90eXBlX2lkIjoiUkVPcnRob1RpbGUiLCJ0b2tlbl90eXBlIjoidHlwZWQtaXRlbSIsImV4cCI6MTQ3Mzc1MDczOCwiaXRlbV9pZCI6IjIwMTYwNzA3XzE5NTE0N18xMDU3OTE2X1JhcGlkRXllLTEiLCJhc3NldF90eXBlIjoidmlzdWFsIn0.lhRgqIggvnRoCgUVX3hgaNYDQIdU09wVaImxv3a_vuGjfzC7_OteYeViboeiZYBH2_eMdWT5ZWDz2BZiAWkXlQ"
```

You can CURL that direct link or copy it into a web browser to download the image.

```sh
curl -L \
"https://api.planet.com/data/v1/download?token=eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwUDNCNU9aYVFKUnN2WGsydmF3UVpLL2ZWci9DZWk0bG82OGJuT2NRR2laZ01EcFBTUnpsSWdHNGlZM2R5YTZWQ2xHdDROeFBka29Kb295a1BvdktPUT09IiwiaXRlbV90eXBlX2lkIjoiUkVPcnRob1RpbGUiLCJ0b2tlbl90eXBlIjoidHlwZWQtaXRlbSIsImV4cCI6MTQ3Mzc1MDczOCwiaXRlbV9pZCI6IjIwMTYwNzA3XzE5NTE0N18xMDU3OTE2X1JhcGlkRXllLTEiLCJhc3NldF90eXBlIjoidmlzdWFsIn0.lhRgqIggvnRoCgUVX3hgaNYDQIdU09wVaImxv3a_vuGjfzC7_OteYeViboeiZYBH2_eMdWT5ZWDz2BZiAWkXlQ" \
> redding.tiff
```

You should now be the proud owner of a brand new visual RapidEye asset.

[high res tiff](../images/redding1.tiff)

![](../images/redding1.jpg)

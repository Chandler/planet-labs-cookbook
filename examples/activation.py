import os
import requests
from requests.auth import HTTPBasicAuth

item_id = "20160707_195147_1057916_RapidEye-1"
item_type = "REOrthoTile"
asset_type = "visual"

# request an item
item = \
  requests.get(
    ("https://api.planet.com/data/v1/item-types/" +
    "{}/items/{}/assets/").format(item_type, item_id),
    auth=HTTPBasicAuth(os.environ['PLANET_API_KEY'], ''))

# extract the activation url from the item for the desired asset
item_activation_url = item.json()[asset_type]["_links"]["activate"]

# request activation
response = \
  requests.post(
    item_activation_url,
    auth=HTTPBasicAuth(os.environ['PLANET_API_KEY'], ''))

print response.status_code

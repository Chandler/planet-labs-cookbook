import os
import requests
from requests.auth import HTTPBasicAuth

# our demo filter that filtrs by geometry, date and cloud cover
from demo_filters import composed_filter

# Stats API request object
search_endpoint_request = {
  "item_types": ["REOrthoTile"],
  "filter": composed_filter
}

result = \
  requests.post(
    'https://api.planet.com/data/v1/quick-search',
    auth=HTTPBasicAuth(os.environ['PLANET_API_KEY'], ''),
    json=search_endpoint_request)

print result.text
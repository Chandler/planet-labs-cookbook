import os
import requests
from requests.auth import HTTPBasicAuth

# our demo filter that filtrs by geometry, date and cloud cover
from demo_filters import composed_filter

# Stats API request object
stats_endpoint_request = {
  "interval": "day",
  "item_types": ["REOrthoTile"],
  "filter": composed_filter
}

# fire off the POST request
result = \
  requests.post(
    'https://api.planet.com/data/v1/stats',
    auth=HTTPBasicAuth(os.environ['PLANET_API_KEY'], ''),
    json=stats_endpoint_request)

print result.text
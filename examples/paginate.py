import os
import requests
from requests.auth import HTTPBasicAuth

# grab a whole week
date_range_filter = {
  "type": "DateRangeFilter",
  "field_name": "acquired",
  "config": {
    "gte": "2016-07-01T00:00:00.000Z",
    "lte": "2016-07-07T00:00:00.000Z"
  }
}

search_endpoint_request = {
  "item_types": ["REOrthoTile"],
  "filter": date_range_filter
}

result = \
  requests.post(
    'https://api.planet.com/data/v1/quick-search',
    auth=HTTPBasicAuth(os.environ['PLANET_API_KEY'], ''),
    json=search_endpoint_request)

print result.text
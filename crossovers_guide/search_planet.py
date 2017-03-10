import os
import requests
from requests.auth import HTTPBasicAuth

def search(
  geometry,
  date_start="2001-07-01T00:00:00.000Z",
  date_end="2018-08-01T00:00:00.000Z",
  item_types=["PSScene3Band"]):

  geometry_filter = {
    "type": "GeometryFilter",
    "field_name": "geometry",
    "config": geometry
  }

  date_range_filter = {
    "type": "DateRangeFilter",
    "field_name": "acquired",
    "config": {
      "gte": date_start,
      "lte": date_end
    }
  }

  combined_filter = {
    "type": "AndFilter",
    "config": [geometry_filter, date_range_filter]
  }

  search_endpoint_request = {
    "item_types": item_types,
    "filter": combined_filter
  }

  result = \
    requests.post(
      'https://api.planet.com/data/v1/quick-search',
      auth=HTTPBasicAuth(os.environ['PLANET_API_KEY'], ''),
      json=search_endpoint_request)

  return result.json()["features"]
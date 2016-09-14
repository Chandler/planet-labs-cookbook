import os
import requests

session = requests.Session()
session.auth = (os.environ['PLANET_API_KEY'], '')

# this large search filter produces all PlanetScope imagery for 1 day
very_large_search = {
  "name": "very_large_search",
  "item_types": ["PSOrthoTile"],
  "filter": {
      "type": "DateRangeFilter",
      "field_name": "acquired",
      "config": {
        "gte": "2016-07-01T00:00:00.000Z",
        "lte": "2016-07-02T00:00:00.000Z"
      }
    }
}

# Create a Saved Search
saved_search = \
    session.post(
        'https://api.planet.com/data/v1/searches/',
        json=very_large_search)

# after you create a search, save the id. This is what is needed
# to execute the search.
saved_search_id = saved_search.json()["id"]

# What we want to do with each page of search results
# in this case, just print out each id
def handle_page(page):
    for item in page["features"]:
        print item["id"]

# How to Paginate:
# 1) Request a page of search results
# 2) do something with the page of results
# 3) if there is more data, recurse and call this method on the next page.
def fetch_page(search_url):
    page = session.get(search_url).json()
    handle_page(page)
    next_url = page["_links"].get("_next")
    if next_url:
        fetch_page(next_url)

first_page = \
    ("https://api.planet.com/data/v1/searches/{}" +
        "/results?_page_size={}").format(saved_search_id, 250)

# kick off the pagination
fetch_page(first_page)


import os
import requests
from multiprocessing.dummy import Pool as ThreadPool

# setup auth
session = requests.Session()
session.auth = (os.environ['PLANET_API_KEY'], '')

def activate_item(item_id):
    print "activating: " + item_id

    # request an item
    item = session.get(
        ("https://api.planet.com/data/v1/item-types/" +
        "{}/items/{}/assets/").format("PSOrthoTile", item_id))

    # request activation
    session.post(
        item.json()["visual"]["_links"]["activate"])

# An easy way to parallise I/O bound operations in Python
# is to use a ThreadPool.
parallelism = 5
thread_pool = ThreadPool(parallelism)

# Open up a file of ids that we have already retrieved from a search
with open('examples/1000_PSOrthoTile_ids.txt') as f:
    item_ids = f.read().splitlines()[:100] # only grab 100

# In this example, all items will be sent to the `activate_item` function
# but only 5 will be running at once
thread_pool.map(activate_item, item_ids)

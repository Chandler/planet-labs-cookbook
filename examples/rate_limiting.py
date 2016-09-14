import os
import requests
from multiprocessing.dummy import Pool as ThreadPool
from retrying import retry

# setup auth
session = requests.Session()
session.auth = (os.environ['PLANET_API_KEY'], '')

@retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000)
def activate_item(item_id):
    print "attempting to activate: " + item_id

    # request an item
    item = session.get(
        ("https://api.planet.com/data/v1/item-types/" +
        "{}/items/{}/assets/").format("PSOrthoTile", item_id))

    if item.status_code == 402:
        raise Exception("rate limit error")

    # request activation
    result = session.post(
        item.json()["visual"]["_links"]["activate"])

    if result.status_code == 402:
        raise Exception("rate limit error")

    print "activation succeeded for item " + item_id

parallelism = 50

thread_pool = ThreadPool(parallelism)

with open('examples/1000_PSOrthoTile_ids.txt') as f:
    item_ids = f.read().splitlines()[:400] # only grab 100

thread_pool.map(activate_item, item_ids)

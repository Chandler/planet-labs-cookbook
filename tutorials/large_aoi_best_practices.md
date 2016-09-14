![](../images/large_aoi.png)

# Large AOI Best Practices

Using the Planet API against a large AOI can be tricky, you will find that it's a fine balance between going too slow and you quickly hit API rate limits. Here are some common patterns for dealing with a large amount of items.

* [Paginate Through a Large Search](#paginate)
* [Parallelising Requests](#parallel)
* [Working with Rate Limits](#rate)

<a name="paginate"></a>
## Paginate Through a Large Search

When a search returns more then 250 results those results will be broken up into several pages. You must request each page seperately, below is a common pagination pattern.

[examples/pagination.py](../examples/pagination.py)

```python
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
        "/results?_page_size={}").format(saved_search_id, 5)

# kick off the pagination
fetch_page(first_page)


```

```sh
➜ python examples/pagination.py
219842_2261109_2016-07-01_0c2b
219842_1962716_2016-07-01_0c2b
219842_1962713_2016-07-01_0c2b
219842_1962613_2016-07-01_0c2b
219842_1962714_2016-07-01_0c2b
...
```

<a name="parallel"></a>
## Parallelising Requests

If you need to perform a large number of API operations, such as activating many items, your request rate can be improved by sending requests in parallel.

In Python this can be done using a ThreadPool. The size of the ThreadPool will define the parallism of requests.
> Due to Python's architecture ThreadPools are most useful when doing I/O bound operations, like talking to an API. If the operations were CPU bound, this would not be a good idea See: [GIL](http://www.dabeaz.com/python/UnderstandingGIL.pdf).

Note: If you inrease the request rate too much you will run into rate limiting, [see the next section](#rate) for how to deal with that.

[examples/parallelism.py](../examples/parallelism.py)

```python
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

```

```sh
➜ python examples/parallelism.py
activating: 219842_2261109_2016-07-01_0c2b
 activating: 217416_1962722_2016-07-01_0c2b
activating: 219842_1962614_2016-07-01_0c2b
activating: 217416_1761305_2016-07-01_0c2b
 activating: 217416_1660809_2016-07-01_0c2b
 ...
```

<a name="rate"></a>
## Working with Rate Limiting

If you handle them correctly, rate limiting errors will be a normal and useful part of working with the API. 

The Planet API responds with ```HTTP 402``` when your request has been denied due to exceeding rate limits.

The following example shows you how to identify a rate limit error and then retry with an exponential backoff. An exponential backoff means that you wait for exponentially longer intervals between each retry of a single failing request.


The retrying library provides a decorator that you can add to any method to give it various types of retries.

[examples/rate_limit.py](../examples/rate_limit.py)

```python
import os
import requests
from multiprocessing.dummy import Pool as ThreadPool
from retrying import retry

# setup auth
session = requests.Session()
session.auth = (os.environ['PLANET_API_KEY'], '')

# "Wait 2^x * 1000 milliseconds between each retry, up to 10
# seconds, then 10 seconds afterwards"
@retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000)
def activate_item(item_id):
    print "attempting to activate: " + item_id

    # request an item
    item = session.get(
        ("https://api.planet.com/data/v1/item-types/" +
        "{}/items/{}/assets/").format("PSOrthoTile", item_id))

	 # raise an exception to trigger the retry
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
```


```sh
➜ python examples/rate_limiting.py
attempting to activate: 217416_1661222_2016-07-01_0c2b
attempting to activate: 217416_1962721_2016-07-01_0c2b
attempting to activate: 217416_1661320_2016-07-01_0c2b
attempting to activate: 217416_1458713_2016-07-01_0c2b
 attempting to activate: 217416_1761305_2016-07-01_0c2b
activation succeeded for item 217416_1761714_2016-07-01_0c2b
 activation succeeded for item 217416_2062808_2016-07-01_0c2b
 attempting to activate: 217416_1761712_2016-07-01_0c2b
attempting to activate: 217416_1962820_2016-07-01_0c2b
activation succeeded for item 217416_1153521_2016-07-01_0c2b
```



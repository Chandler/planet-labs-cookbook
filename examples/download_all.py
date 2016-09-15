import argparse
import os
import requests

# our demo filter that filters by geometry, date and cloud cover
from demo_filters import redding_reservoir

ASSET_URL = "https://api.planet.com/data/v1/item-types/{}/items/{}/assets/"
ASSET_TYPE = 'visual'
ITEM_TYPE = 'REOrthoTile'
SEARCH_URL = 'https://api.planet.com/data/v1/quick-search'

# Search API request object
SEARCH_PAYLOAD = {"item_types": [ITEM_TYPE], "filter": redding_reservoir}

# setup auth
SESSION = requests.Session()
SESSION.auth = (os.environ['PLANET_API_KEY'], '')


def run_search(search_request):
    result = SESSION.post(SEARCH_URL, json=search_request)

    return [f['id'] for f in result.json()['features']]


def simple_activate(item_id):
    item = SESSION.get(ASSET_URL.format('REOrthoTile', item_id))
    item_activation_url = item.json()[ASSET_TYPE]["_links"]["activate"]

    print 'Activating visual for {}'.format(item_id)

    result = SESSION.post(item_activation_url)
    if result.status_code != 204:
        print 'Activation error'
        return False
    else:
        print 'Activation process started successfully'
        return True


def check_activation(item_id):
    item = SESSION.get(ASSET_URL.format('REOrthoTile', item_id))
    status = item.json()['visual']['status']
    print '{}: {}'.format(item_id, status)

    if status == 'active':
        return True
    else:
        return False


def download_image(url, path, item_id):
    local_path = os.path.join(path, item_id + '.tif')

    # memory-efficient download, per
    # stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
    r = requests.get(url)
    f = open(local_path, 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024):
        if chunk:  # filter out keep-alive new chunks
            f.write(chunk)
    f.close()

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--search', action="store_true")
    parser.add_argument('--check', action="store_true")
    parser.add_argument('--activate', action="store_true")
    parser.add_argument('--download')

    args = parser.parse_args()

    if args.search:
        item_ids = run_search(SEARCH_PAYLOAD)
        print '%d available images' % len(item_ids)

    if args.activate:
        results = []

        ids = run_search(SEARCH_PAYLOAD)

        for item_id in ids:
            result = simple_activate(item_id)
            results.append(result)

        msg = 'Requested activation for {} of {} items'
        print msg.format(results.count(True), len(results))

    if args.check:
        results = []

        ids = run_search(SEARCH_PAYLOAD)

        for item_id in ids:
            result = check_activation(item_id)
            results.append(result)

        msg = '{} of {} items are active'
        print msg.format(results.count(True), len(results))

    if args.download:
        path = args.download
        results = []

        item_ids = run_search(SEARCH_PAYLOAD)

        for item_id in item_ids:
            item = SESSION.get(ASSET_URL.format('REOrthoTile', item_id))
            download_url = item.json()['visual']['location']
            result = download_image(download_url, '/tmp', item_id)
            results.append(result)
        msg = 'Downloaded {} files to {}:'
        print msg.format(results.count(True), path)

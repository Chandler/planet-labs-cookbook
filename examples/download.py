#!/usr/bin/env python

import argparse
import os
import requests
import json
from retrying import retry


ASSET_URL = "https://api.planet.com/data/v1/item-types/{}/items/{}/assets/"
SEARCH_URL = 'https://api.planet.com/data/v1/quick-search'

# set up auth
SESSION = requests.Session()
SESSION.auth = (os.environ['PLANET_API_KEY'], '')


@retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000)
def run_search(search_request):
    result = SESSION.post(SEARCH_URL, json=search_request)

    if result.status_code == 402:
        raise Exception("rate limit error")

    return [f['id'] for f in result.json()['features']]


@retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000)
def activate(item_id, item_type, asset_type):
    result = SESSION.get(ASSET_URL.format(item_type, item_id))
    if result.status_code == 402:
        raise Exception("rate limit error")

    item_activation_url = result.json()[asset_type]["_links"]["activate"]

    print 'Activating visual for {}'.format(item_id)
    result = SESSION.post(item_activation_url)
    if result.status_code == 402:
        raise Exception("rate limit error")
    else:
        print 'Activation process started successfully'
        return True


@retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000)
def check_activation(item_id, item_type, asset_type):
    result = SESSION.get(ASSET_URL.format(item_type, item_id))

    if result.status_code == 402:
        raise Exception("rate limit error")

    status = result.json()[asset_type]['status']
    print '{}: {}'.format(item_id, status)

    if status == 'active':
        return True
    else:
        return False


@retry(
    wait_exponential_multiplier=1000,
    wait_exponential_max=10000)
def download(url, path, item_id, asset_type, overwrite):
    fname = '{}_{}.tif'.format(item_id, asset_type)
    local_path = os.path.join(path, fname)

    if not overwrite and os.path.exists(local_path):
        print 'File {} exists - skipping ...'.format(local_path)
    else:
        print 'Downloading file to {}'.format(local_path)
        # memory-efficient download, per
        # stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
        result = requests.get(url)

        if result.status_code == 402:
            raise Exception("rate limit error")

        f = open(local_path, 'wb')
        for chunk in result.iter_content(chunk_size=512 * 1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
        f.close()

    return True


def process_activation(func, search_payload, item_type, asset_type):
    results = []

    ids = run_search(search_payload)

    for item_id in ids:
        result = func(item_id, item_type, asset_type)
        results.append(result)

    return results


def process_download(path, search_payload, item_type, asset_type, overwrite):
    results = []

    item_ids = run_search(search_payload)

    # ensure directory structure exists
    try:
        os.makedirs(path)
    except OSError:
        pass

    # now start downloading each file
    for item_id in item_ids:
        result = SESSION.get(ASSET_URL.format(item_type, item_id))

        if result.json()[asset_type]['status'] == 'active':
            download_url = result.json()[asset_type]['location']
            result = download(download_url, path, item_id, asset_type, overwrite)
        else:
            result = False

        results.append(result)

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--search', action="store_true")
    parser.add_argument('--check', action="store_true")
    parser.add_argument('--activate', action="store_true")
    parser.add_argument('--download', help="Path where downloaded files should be stored")
    parser.add_argument('--overwrite', help="Overwrite existing downloads", action='store_true')
    parser.add_argument('query', help="Path to json file containing query")
    parser.add_argument('item', help="Item type (e.g. REOrthoTile or PSOrthoTile")
    parser.add_argument('asset', help="Asset type (e.g. visual, analytic, analytic_xml")

    args = parser.parse_args()

    # load query json file
    with open(args.query, 'r') as fp:
        query = json.load(fp)

    # Search API request object
    search_payload = {"item_types": [args.item], "filter": query}

    if args.search:
        results = run_search(search_payload)
        print '%d available images' % len(results)

    if args.activate:
        results = process_activation(activate, search_payload, args.item,
                                     args.asset)
        msg = 'Requested activation for {} of {} items'
        print msg.format(results.count(True), len(results))

    # check activation status of all data returned by search query
    if args.check:
        results = process_activation(check_activation, search_payload, args.item,
                                     args.asset)

        msg = '{} of {} items are active'
        print msg.format(results.count(True), len(results))

    # download all data returned by search query
    if args.download:
        results = process_download(args.download, search_payload, args.item,
                                   args.asset, args.overwrite)
        msg = 'Successfully downloaded {} of {} files to {}. {} were not activated yet.'
        print msg.format(results.count(True), len(results), args.download, results.count(False))

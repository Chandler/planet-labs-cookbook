from usgs import api
import json
import os
import sys

usgs_api_key = api.login(
    os.environ["EARTH_EXPLORER_USERNAME"],
    os.environ["EARTH_EXPLORER_PASSWORD"])

scenes = \
    api.search(
        'EO1_HYP_PUB',
        'EE',
        api_key=usgs_api_key,
        start_date='2017-02-01',
        end_date='2017-03-01',
        extended=True)

with open(sys.argv[1], "w") as f:
    f.write(json.dumps(scenes))


import json
import search_planet
from datetime import datetime, timedelta
import dateutil.parser
import requests
import sys

CROSS_OVER_WINDOW_HOURS=4

input_path = sys.argv[1]

output_path = sys.argv[2]

def usgs_record_to_geojson(record):
    """
    Converts a USGS json record into a geometry object
    that can be used to search the Planet API.
    """
    return {
      "type": "Polygon",
      "coordinates": [
        [
          [
            record["upperLeftCoordinate"]["longitude"],
            record["upperLeftCoordinate"]["latitude"],
          ],
          [
            record["upperRightCoordinate"]["longitude"],
            record["upperRightCoordinate"]["latitude"],
          ],
          [
            record["lowerRightCoordinate"]["longitude"],
            record["lowerRightCoordinate"]["latitude"],
          ],
          [
            record["lowerLeftCoordinate"]["longitude"],
            record["lowerLeftCoordinate"]["latitude"],
          ],
          [
            record["upperLeftCoordinate"]["longitude"],
            record["upperLeftCoordinate"]["latitude"],
          ]
        ]
      ]
    }

def calculate_crossover_window(image_acquisition_time, delta_hours):
    """
    Given an acquisition time, calculate a window around it to look
    for crossovers in
    """
    window_start = (image_acquisition_time - timedelta(hours=delta_hours/2)).strftime("%Y-%m-%dT%H:%M:%S.%f%zZ")
    window_end = (image_acquisition_time + timedelta(hours=delta_hours/2)).strftime("%Y-%m-%dT%H:%M:%S.%f%zZ")
    return (window_start, window_end)

def time_between_dates(eo1_date, planet_date):
    td = abs(eo1_date - planet_date)
    return "{} days {} hours {} minutes".format(td.days, td.seconds//3600, (td.seconds//60)%60)

def find_crossovers(record):
    # build a geometry object representing the hyperion image
    geometry = usgs_record_to_geojson(record)

    # parse the hyperion date
    usgs_image_acquisition_time = \
      datetime.strptime(record["extended"]["Scene Start Time"], '%Y:%j:%H:%M:%S.%f')

    # calculate the time bounds for the crossover search
    window_start, window_end = \
      calculate_crossover_window(
        usgs_image_acquisition_time,
        CROSS_OVER_WINDOW_HOURS)

    # search the planet API
    search_results = \
      search_planet.search(geometry, window_start, window_end)

    crossovers = []
    if len(search_results) > 0:
      for result in search_results:
          planet_image_acquisition_time = \
            dateutil.parser.parse(result["properties"]["acquired"]).replace(tzinfo=None)

          acquisition_offset = \
            time_between_dates(
              usgs_image_acquisition_time,
              planet_image_acquisition_time)

          crossover = {
             "id": result["id"],
             "acquisition_offset": acquisition_offset,
             "properties":  result["properties"],
          }
          crossovers.append(crossover)
    return crossovers

with open(input_path, "r") as f:
    usgs_records = json.loads(f.read())
    crossover_groups = []
    for usgs_record in usgs_records:

      crossovers = find_crossovers(usgs_record)

      if(len(crossovers) > 0):
        print "{}: {} crossovers".format(
          usgs_record["displayId"], len(crossovers))
        crossover_groups.append({
           "usgs_id": usgs_record["displayId"],
           "crossovers": find_crossovers(usgs_record)
        })

    with open(output_path, 'w') as outfile:
      outfile.write(json.dumps(crossover_groups))




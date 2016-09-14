
![](images/header1.jpg)

## Planet Labs API Cookbook

#### Tutorials

* [API v1 Walkthrough Part 1, Search](tutorials/intro_part_1_search.md)
*  [API v1 Walkthrough Part 2, Activation and Downloading](tutorials/intro_part_2_activation.md) 
*  [Large AOI Best Practices](tutorials/large_aoi_best_practices.md)
	1. [Paginate Through a Large Search](tutorials/large_aoi_best_practices.md#paginate)
	2. [Parallelising Requests](tutorials/large_aoi_best_practices.md#parallel)
	3. [Working with Rate Limits](tutorials/large_aoi_best_practices.md#rate)

## API Access
These tutorials assume that you have a Planet API key. Currently anyone can sign up for a limited access key at [planet.com/products/open-california](https://www.planet.com/products/open-california/). This will give you access to free imagery in California only. (Note, Open California approval is not instantanious)

Once you have an API key, add the key to your shell environment:


```sh
export PLANET_API_KEY=a3a64774d30c4749826b6be445489d3b # (not a real key)
```

## Development Environment

These tutorials use the following tools:
 
 * Python 2
 * [requests](http://docs.python-requests.org/en/master/) - (pip install requests)
 * [retrying](https://github.com/rholder/retrying) - (pip install retrying)
 * cURL
 * [jq](https://stedolan.github.io/jq/) - a very useful command line tool for maniuplating and displaying JSON.
 * (optional) [geojsonio-cli](https://github.com/mapbox/geojsonio-cli) - quickly view geometries in geojson.io

Most examples pipe the JSON api output to jq and filter for a specific field. You may want to also remove the jq filter to familarize yourelf with the complete API objects.


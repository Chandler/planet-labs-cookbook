![](../images/large_aoi.png)

# Large AOI Best Practices

Using the Planet API against a large AOI can be tricky, you will find that you quickly hit API rate limits. Here are some common patterns for dealing with a large amount of items.

* [Paginate Through a Search](#paginate)
* [Bulk Activate](#activate)
* [Poll Until Ready](#poll)


## Paginate Through a Search
If there are more than 250 items in your search result you will need to paginate to see them all.


[examples/paginate.py](../examples/paginate.py)

## Bulk Activate

## Poll Until Ready
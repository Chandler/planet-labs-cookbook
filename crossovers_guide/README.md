This project contains tooling for finding satellite crossovers. For a complete explanation see the blog post

This is not ~quality software~ or a real tool, it's just a few scripts


Run everything like this:

```
export EARTH_EXPLORER_USERNAME=myuser
export EARTH_EXPLORER_PASSWORD=mypass
export PLANET_API_KEY=mykey

python search_usgs.py data/usgs_results.json

python find_crossovers.py data/usgs_results.json data/crossovers.json

python render_crossovers.py data/crossovers.json data/renders
```
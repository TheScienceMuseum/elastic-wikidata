# Changelog

All notable changes documented below.

## 0.3.1

- **fix:** property values without types are ignored
- **enhancement:** refresh is disabled for the duration of data load by default, using `--disable_refresh` flag. This is beneficial for large datasets or low-resource machines as refreshing the search index is CPU-intensive and can cause the data load to freeze.

## 0.3.0

- add changeable timeout for `wbgetentities` GET request
- handle more Wikidata claims than just QIDs
- generate User Agent from request in line with Wikidata guidelines
- make Wikidata-related methods importable (rather than just runnable from CLI)

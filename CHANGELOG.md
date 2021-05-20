# Changelog

All notable changes documented below.

## 1.0.0
- **enhancement (breaking change):** properties now passed as whitespace-separated list rather than comma-separated. They can also be passed through a config file by giving the `--properties` option a filename to a file that exists.
- **stability improvements:** `elasticsearch.helpers.streaming_bulk` now used instead of `elasticsearch.helpers.parallel_bulk` due to issues with memory usage of the latter. Bulk load now retries on timeout.

## 0.3.7
- **fix:** reading from JSON dump forces utf-8
## 0.3.6

- **fix:** handles documents which are missing any of *labels/aliases/descriptions/claims* fields.
- **enhancement:** `wd_entities.simplify_wbgetentities_result` gives the option to return the redirected QID for Wikidata pages which redirect. By default it returns the undirected QID: the same one that was passed into the function.

## 0.3.5

- **fix:** `wd_entities.simplify_wbgetentities_result` can handle type *quantity*, and returns the value of *amount*.

## 0.3.4

- **enhancement:** `wd_entities.get_entities` now has a `get_labels` method to get labels for a list of QIDs in a particular language using the wbgetentities API.

## 0.3.2

- **enhancement:** add `labels_aliases` field for faster text search of both labels and aliases using an [Elasticsearch match query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html)

## 0.3.1

- **fix:** property values without types are ignored
- **enhancement:** refresh is disabled for the duration of data load by default, using `--disable_refresh` flag. This is beneficial for large datasets or low-resource machines as refreshing the search index is CPU-intensive and can cause the data load to freeze.

## 0.3.0

- add changeable timeout for `wbgetentities` GET request
- handle more Wikidata claims than just QIDs
- generate User Agent from request in line with Wikidata guidelines
- make Wikidata-related methods importable (rather than just runnable from CLI)

# Elastic Wikidata

Simple CLI tools to load a subset of Wikidata into Elasticsearch.

## Why?

Running text search programmatically on Wikidata means using the MediaWiki query API, either [directly](https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=John_Snow&srlimit=10&srprop=size&formatversion=2) or [through the Wikidata query service/SPARQL](https://query.wikidata.org/#SELECT%20%2a%20WHERE%20%7B%0A%20%20SERVICE%20wikibase%3Amwapi%20%7B%0A%20%20%20%20%20%20bd%3AserviceParam%20wikibase%3Aendpoint%20%22en.wikipedia.org%22%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3Aapi%20%22Search%22%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20mwapi%3Asrsearch%20%22John%20Snow%22.%0A%20%20%20%20%20%20%3Ftitle%20wikibase%3AapiOutput%20mwapi%3Atitle.%0A%20%20%7D%0A%20%20%20hint%3APrior%20hint%3ArunLast%20%22true%22.%0A%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22.%20%7D%0A%7D%20LIMIT%2020).

There are a couple of reasons you may not want to do this when running searches programmatically:

* *time constraints/large volumes:* APIs are rate-limited, and you can only do one text search per SPARQL query
* *better search:* using Elasticsearch allows for more flexible and powerful text search capabilities

## Installation

1. Download 
2. `cd` into root 
3. `pip install .`

Eventually this will be hosted on pip.

## Setup

elastic-wikidata needs the Elasticsearch credentials `ELASTICSEARCH_CLUSTER`, `ELASTICSEARCH_USER` and `ELASTICSEARCH_PASSWORD` to connect to your ES instance. You can set these in one of two ways:

1. Using environment variables: `export ELASTICSEARCH_CLUSTER=https://...` etc
2. Using config.ini: pass the `-c` parameter followed by a path to an ini file containing your Elasticsearch credentials. [Example here](./config.sample.ini).

## Usage

Once installed the package is accessible through the keyword `ew`. A call is structured as follows:

``` bash
ew <option> <arguments>
```

### Loading from Wikidata dump (.ndjson)

``` bash
ew dump -p <path_to_json> <other_options>
```

This is useful if you want to create one or more large subsets of Wikidata in different Elasticsearch indexes (millions of entities).

1. Download the complete Wikidata dump (latest-all.json.gz from [here](https://dumps.wikimedia.org/wikidatawiki/entities/)). This is a *large* file: 87GB on 07/2020.
2. Use [maxlath](https://github.com/maxlath)'s [wikibase-dump-filter](https://github.com/maxlath/wikibase-dump-filter/) to create a subset of the Wikidata dump.
3. Run `ew dump` with flag `-p` pointing to the JSON subset. You might want to test it with a limit (using the `-l` flag) first, i.e. `-l 100` only imports the first 100 records.

# Elastic Wikidata

Simple CLI tools to load a subset of Wikidata into Elasticsearch. Part of the [Heritage Connector](https://www.sciencemuseumgroup.org.uk/project/heritage-connector/) project.

- [Why?](#why)
- [Installation](#installation)
- [Setup](#setup)
- [Usage](#usage)
  - [Loading from Wikidata dump (.ndjson)](#loading-from-wikidata-dump-ndjson)
  - [Loading from SPARQL query](#loading-from-sparql-query)
  
</br>

![PyPI - Downloads](https://img.shields.io/pypi/dm/elastic-wikidata)
![GitHub last commit](https://img.shields.io/github/last-commit/thesciencemuseum/elastic-wikidata)
![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/thesciencemuseum/elastic-wikidata)

## Why?

Running text search programmatically on Wikidata means using the MediaWiki query API, either [directly](https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=John_Snow&srlimit=10&srprop=size&formatversion=2) or [through the Wikidata query service/SPARQL](https://query.wikidata.org/#SELECT%20%2a%20WHERE%20%7B%0A%20%20SERVICE%20wikibase%3Amwapi%20%7B%0A%20%20%20%20%20%20bd%3AserviceParam%20wikibase%3Aendpoint%20%22en.wikipedia.org%22%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20wikibase%3Aapi%20%22Search%22%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20mwapi%3Asrsearch%20%22John%20Snow%22.%0A%20%20%20%20%20%20%3Ftitle%20wikibase%3AapiOutput%20mwapi%3Atitle.%0A%20%20%7D%0A%20%20%20hint%3APrior%20hint%3ArunLast%20%22true%22.%0A%20%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22en%22.%20%7D%0A%7D%20LIMIT%2020).

There are a couple of reasons you may not want to do this when running searches programmatically:

- *time constraints/large volumes:* APIs are rate-limited, and you can only do one text search per SPARQL query
- *better search:* using Elasticsearch allows for more flexible and powerful text search capabilities.<sup>*</sup> We're using our own Elasticsearch instance to do nearest neighbour search on embeddings, too. 

*<sup>&ast;</sup> [CirrusSearch](https://www.mediawiki.org/wiki/Extension:CirrusSearch) is a Wikidata extension that enables direct search on Wikidata using Elasticsearch, if you require powerful search and are happy with the rate limit.*

## Installation

from pypi: `pip install elastic_wikidata`

from repo:

1. Download
2. `cd` into root
3. `pip install -e .`

## Setup

elastic-wikidata needs the Elasticsearch credentials `ELASTICSEARCH_CLUSTER`, `ELASTICSEARCH_USER` and `ELASTICSEARCH_PASSWORD` to connect to your ES instance. You can set these in one of three ways:

1. Using environment variables: `export ELASTICSEARCH_CLUSTER=https://...` etc
2. Using config.ini: pass the `-c` parameter followed by a path to an ini file containing your Elasticsearch credentials. [Example here](./config.sample.ini).
3. Pass each variable in at runtime using options `--cluster/-c`, `--user/-u`, `--password/-p`.

## Usage

Once installed the package is accessible through the keyword `ew`. A call is structured as follows:

``` bash
ew <task> <options>
```

*Task* is either:

- `dump`: [load data from Wikidata JSON dump](#loading-from-wikidata-dump-ndjson), or
- `query`: [load data from SPARQL query](#loading-from-sparql-query).

A full list of options can be found with `ew --help`, but the following are likely to be useful:

- `--index/-i`: the index name to push to. If not specified at runtime, elastic-wikidata will prompt for it
- `--limit/-l`: limit the number of records pushed into ES. You might want to use this for a small trial run before importing the whole thing.
- `--properties/-prop`: pass a comma-separated list of properties to include in the ES index. E.g. *p31,p21*.
- `--language/-lang`: [Wikimedia language code](https://www.wikidata.org/wiki/Help:Wikimedia_language_codes/lists/all). Only one supported at this time.

### Loading from Wikidata dump (.ndjson)

``` bash
ew dump -p <path_to_json> <other_options>
```

This is useful if you want to create one or more large subsets of Wikidata in different Elasticsearch indexes (millions of entities).

**Time estimate:** Loading all ~8million humans into an AWS Elasticsearch index took me about 20 minutes. Creating the humans subset using `wikibase-dump-filter` took about 3 hours using its [instructions for parallelising](https://github.com/maxlath/wikibase-dump-filter/blob/master/docs/parallelize.md).

1. Download the complete Wikidata dump (latest-all.json.gz from [here](https://dumps.wikimedia.org/wikidatawiki/entities/)). This is a *large* file: 87GB on 07/2020.
2. Use [maxlath](https://github.com/maxlath)'s [wikibase-dump-filter](https://github.com/maxlath/wikibase-dump-filter/) to create a subset of the Wikidata dump.
3. Run `ew dump` with flag `-p` pointing to the JSON subset. You might want to test it with a limit (using the `-l` flag) first.

### Loading from SPARQL query

``` bash
ew query -p <path_to_sparql_query> <other_options>
```

For smaller collections of Wikidata entities it might be easier to populate an Elasticsearch index directly from a SPARQL query rather than downloading the whole Wikidata dump to take a subset. `ew query` [automatically paginates SPARQL queries](examples/paginate%20query.ipynb) so that a heavy query like *'return all the humans'* doesn't result in a timeout error.

**Time estimate:** Loading 10,000 entities into Wikidata into an AWS hosted Elasticsearch index took me about 6 minutes.

1. Write a SPARQL query and save it to a text/.rq file. See [example](queries/humans.rq).
2. Run `ew query` with the `-p` option pointing to the file containing the SPARQL query. Optionally add a `--page_size` for the SPARQL query.

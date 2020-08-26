from elastic_wikidata import dump_to_es, sparql_to_es
from elastic_wikidata.config import runtime_config
import click
from configparser import ConfigParser


@click.command()
@click.argument("source", nargs=1)
@click.option("--path", "-p", type=click.Path(exists=True))
@click.option(
    "--cluster", envvar="ELASTICSEARCH_CLUSTER", help="Elasticsearch cluster URL"
)
@click.option("--user", envvar="ELASTICSEARCH_USER", help="Elasticsearch username")
@click.option(
    "--password", envvar="ELASTICSEARCH_PASSWORD", help="Elasticsearch password"
)
@click.option(
    "--agent_contact",
    "-contact",
    envvar="WIKIMEDIA_AGENT_CONTACT",
    help="(optional) Contact details to add to the User Agent header for Wikidata requests",
    default=None,
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    help="Path to .ini file containing Elasticsearch credentials",
)
@click.option(
    "--index",
    "-i",
    prompt="Elasticsearch index",
    help="Name of Elasticsearch index to load into",
)
@click.option(
    "--limit", "-l", type=int, help="(optional) Limit the number of entities loaded in"
)
@click.option("--page_size", type=int, help="Page size for SPARQL query.", default=100)
@click.option(
    "--language", "-lang", type=str, help="Language (Wikimedia language code)"
)
@click.option(
    "--properties",
    "-prop",
    type=str,
    help="One or more Wikidata property e.g. p31 or p31,p21. Not case-sensitive",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    help="Timeout for Wikidata requests (seconds)",
    default=6,
)
def main(
    source,
    path,
    cluster,
    user,
    password,
    agent_contact,
    config,
    index,
    limit,
    page_size,
    language,
    properties,
    timeout,
):

    # get elasticsearch credentials
    if config:
        # read .ini file
        parser = ConfigParser()
        parser.optionxform = str  # make option names case sensitive
        parser.read(config)
        es_credentials = parser._sections["ELASTIC"]
        check_es_credentials(es_credentials)

        runtime_config.add_item(
            {
                "user_agent_contact": parser._sections["HTTP"].get(
                    "CONTACT_DETAILS", None
                )
            }
        )
    else:
        # check environment variables/flags
        es_credentials = {}

        if cluster:
            es_credentials["ELASTICSEARCH_CLUSTER"] = cluster
        if user:
            es_credentials["ELASTICSEARCH_USER"] = user
        if password:
            es_credentials["ELASTICSEARCH_PASSWORD"] = password

        check_es_credentials(es_credentials)

        runtime_config.add_item({"user_agent_contact": agent_contact})

    runtime_config.add_item({"http_timeout": timeout})

    # global flag for all functions that the module is being run through the CLI
    runtime_config.add_item({"cli": True})

    # set kwargs
    kwargs = {}
    if language:
        kwargs["lang"] = language
    if properties:
        kwargs["properties"] = properties.split(",")

    # run job
    if source == "dump":
        load_from_dump(path, es_credentials, index, limit, **kwargs)
    elif source == "query":
        load_from_sparql(path, es_credentials, index, limit, page_size, **kwargs)
    else:
        raise ValueError(f"Argument {source} must be either dump or sparql")


def load_from_dump(path, es_credentials, index, limit, **kwargs):
    if not kwargs:
        kwargs = {}
    if limit:
        kwargs["doc_limit"] = limit

    # limit is used when dumping JSON to Elasticsearch
    d = dump_to_es.processDump(
        dump=path, es_credentials=es_credentials, index_name=index, **kwargs
    )
    d.start_elasticsearch()
    d.dump_to_es()


def load_from_sparql(path, es_credentials, index, limit, page_size=100, **kwargs):
    if not kwargs:
        kwargs = {}

    with open(path, "r") as f:
        query = f.read()

    # limit is used when getting list of entities
    print(f"Getting entities from SPARQL query")
    entity_list = sparql_to_es.get_entities_from_query(
        query, page_size=100, limit=limit
    )

    print(
        f"Retrieving information from wbgetentities API and pushing to ES index {index}"
    )
    d = dump_to_es.processDump(
        dump=entity_list, es_credentials=es_credentials, index_name=index, **kwargs
    )
    d.start_elasticsearch()
    d.dump_to_es()


def check_es_credentials(credentials: dict):
    credentials_present = set(credentials.keys())
    credentials_required = {
        "ELASTICSEARCH_CLUSTER",
        "ELASTICSEARCH_USER",
        "ELASTICSEARCH_PASSWORD",
    }
    missing_credentials = credentials_required - credentials_present

    if len(missing_credentials) > 0:
        raise ValueError(f"Missing Elasticsearch credentials: {missing_credentials}")


if __name__ == "__main__":
    main()

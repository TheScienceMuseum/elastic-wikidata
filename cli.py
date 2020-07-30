import sys

sys.path.append("..")
from elastic_wikidata import dump_to_es
import click
from configparser import ConfigParser


@click.command()
@click.argument("source", nargs=1)
@click.option("--path", "-p", type=click.Path(exists=True))
@click.option("--cluster", envvar="ELASTICSEARCH_CLUSTER")
@click.option("--user", envvar="ELASTICSEARCH_USER")
@click.option("--password", envvar="ELASTICSEARCH_PASSWORD")
@click.option("--config", "-c", type=click.Path(exists=True))
@click.option("--index", "-i", prompt="Elasticsearch index")
@click.option("--limit", "-l", type=int)
def main(source, path, cluster, user, password, config, index, limit):
    # get elasticsearch credentials
    if config:
        # read .ini file
        parser = ConfigParser()
        parser.optionxform = str  # make option names case sensitive
        parser.read(config)
        es_credentials = parser._sections["ELASTIC"]
        check_es_credentials(es_credentials)
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

    #  run job
    if source == "dump":
        load_from_dump(path, es_credentials, index, limit)
    else:
        raise ValueError("source argument must be either dump or sparql")


def load_from_dump(path, es_credentials, index, limit):
    kwargs = {}
    if limit:
        kwargs["doc_limit"] = limit

    d = dump_to_es.processDump(
        dump_path=path, es_credentials=es_credentials, index_name=index, **kwargs
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

import sys

sys.path.append("..")
from elastic_wikidata import dump_to_es
import click
from configparser import ConfigParser


@click.command()
@click.option("--dump", "-d", is_flag=True)
@click.option("--path", "-p", type=click.Path(exists=True))
@click.option("--cluster", envvar="ELASTICSEARCH_CLUSTER")
@click.option("--user", envvar="ELASTICSEARCH_USER")
@click.option("--password", envvar="ELASTICSEARCH_PASSWORD")
@click.option("--config", "-c", type=click.Path(exists=True))
@click.option("--index", "-i", prompt="Elasticsearch index")
@click.option("--limit", "-l", type=int)
def main(dump, path, cluster, user, password, config, index, limit):
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
        missing_vals = [i for i in (cluster, user, password) if not bool(i)]

        if len(missing_vals) > 0:
            raise ValueError(
                f"{len(missing_vals)} values missing from Elasticsearch credentials."
            )
        else:
            es_credentials = {
                "ELASTICSEARCH_CLUSTER": cluster,
                "ELASTICSEARCH_USER": user,
                "ELASTICSEARCH_PASSWORD": password,
            }

    #  run job
    if dump:
        load_from_dump(path, es_credentials, index, limit)


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
    assert all(
        [
            c in credentials
            for c in (
                "ELASTICSEARCH_CLUSTER",
                "ELASTICSEARCH_USER",
                "ELASTICSEARCH_PASSWORD",
            )
        ]
    )


if __name__ == "__main__":
    main()

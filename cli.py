import sys

sys.path.append("..")
from elastic_wikidata import dump_to_es
import click


@click.command()
@click.option("--dump", "-d", is_flag=True)
@click.option("--path", "-p", type=click.Path(exists=True))
@click.option("--index", "-i", prompt="Elasticsearch index")
@click.option("--limit", "-l", type=int)
def main(dump, path, index, limit):
    if dump:
        load_from_dump(path, index, limit)


def load_from_dump(path, index, limit):
    kwargs = {}
    if limit:
        kwargs["doc_limit"] = limit

    d = dump_to_es.processDump(dump_path=path, index_name=index, **kwargs)
    d.start_elasticsearch()
    d.dump_to_es()


if __name__ == "__main__":
    main()

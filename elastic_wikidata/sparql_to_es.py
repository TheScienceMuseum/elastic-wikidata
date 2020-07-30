from elastic_wikidata.sparql_helpers import run_query, paginate_sparql_query
import re
from math import ceil
from itertools import islice
from tqdm.auto import tqdm


def url_to_qid(url: str) -> str:
    """
    Maps Wikidata URL of an entity to QID e.g. http://www.wikidata.org/entity/Q7187777 -> Q7187777.
    """

    return re.findall(r"(Q\d+)", url)[0]


def get_entities_from_query(query, page_size=None, limit=None) -> list:
    """
    Get a list of entities from a query. Optionally:
        paginate the query using page_size
        limit the total number of entities returned using limit

    Returns list of entities in form (Qd+).
    """

    if page_size:
        pages = paginate_sparql_query(query, page_size=page_size)
    else:
        pages = [query]

    if limit:
        page_limit = ceil(limit / page_size)
        pages = islice(pages, page_limit)

    all_entities = []

    for query in tqdm(pages, total=(page_limit or None)):
        res = run_query(query)
        var = res["head"]["vars"][0]
        entities = [url_to_qid(x[var]["value"]) for x in res["results"]["bindings"]]
        all_entities += entities

        # stop when page of query returns fewer items than the page size
        if len(entities) < page_size:
            break

    return all_entities

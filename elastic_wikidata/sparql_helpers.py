from SPARQLWrapper import SPARQLWrapper, JSON
import urllib
import time
from elastic_wikidata.http import generate_user_agent


def run_query(query: str, endpoint_url="https://query.wikidata.org/sparql") -> dict:
    """
    Run a SPARQL query against the Wikidata endpoint. Obeys retry-after headers for sensible bulk querying.

    Args:
        query (str): SPARQL query
        endpoint_url (optional)

    Returns:
        query_result (dict): the JSON result of the query as a dict
    """

    user_agent = generate_user_agent()

    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setMethod("POST")
    sparql.setReturnFormat(JSON)

    try:
        return sparql.query().convert()
    except urllib.error.HTTPError as e:
        if e.code == 429:
            if isinstance(e.headers.get("retry-after", None), int):
                time.sleep(e.headers["retry-after"])
            else:
                time.sleep(10)
            return run_query(query, endpoint_url)
        raise


def paginate_sparql_query(query: str, page_size: int):
    """
    Paginates a SELECT query, returning a generator which yields paginated queries. 
    """

    # check query
    if "select" not in query.lower():
        raise ValueError("Must be a SELECT query")

    if "order by" not in query.lower():
        print(
            "WARNING: no ORDER BY logic in the SPARQL query. This could result in duplicate or missing entities."
        )

    # paginate
    i = 0
    while True:
        yield f"""{query}
        LIMIT {page_size}
        OFFSET {i*page_size}
        """
        i += 1

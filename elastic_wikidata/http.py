import requests
import sys
from elastic_wikidata import __version__ as ew_version


def generate_user_agent(contact_information: str = None):
    """
    Generates user agent string according to Wikidata User Agent Guidelines (https://meta.wikimedia.org/wiki/User-Agent_policy).

    Returns:
        str: user agent string
    """
    v_params = {
        "python": "Python/" + ".".join(str(i) for i in sys.version_info),
        "http_backend": "requests/" + requests.__version__,
        "ew": "Elastic Wikidata bot/" + ew_version,
    }

    if contact_information is not None:
        return f"{v_params['ew']} ({contact_information}) {v_params['http_backend']} {v_params['python']}"
    else:
        print(
            "WARNING: please consider adding contact information to config.ini to improve the User Agent header for Wikidata requests."
        )
        return f"{v_params['ew']} {v_params['http_backend']} {v_params['python']}"

import requests
import sys
from urllib.parse import quote
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
        contact_information = " ".join(
            [process_user_agent_username(i) for i in contact_information.split(" ")]
        )
        return f"{v_params['ew']} ({contact_information}) {v_params['http_backend']} {v_params['python']}"
    else:
        print(
            "WARNING: please consider adding contact information to config.ini to improve the User Agent header for Wikidata requests."
        )
        return f"{v_params['ew']} {v_params['http_backend']} {v_params['python']}"


def process_user_agent_username(username=None):
    """
    **Credit to [pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot)**

    Reduce username to a representation permitted in HTTP headers.

    To achieve that, this function:
    1) replaces spaces (' ') with '_'
    2) encodes the username as 'utf-8' and if the username is not ASCII
    3) URL encodes the username if it is not ASCII, or contains '%'
    """
    if not username:
        return ""

    username = username.replace(" ", "_")  # Avoid spaces or %20.
    try:
        username.encode("ascii")  # just test, but not actually use it
    except UnicodeEncodeError:
        username = quote(username.encode("utf-8"))
    else:
        # % is legal in the default $wgLegalTitleChars
        # This is so that ops know the real pywikibot will not
        # allow a useragent in the username to allow through a hand-coded
        # percent-encoded value.
        if "%" in username:
            username = quote(username)
    return username

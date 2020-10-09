import requests
from tqdm.auto import tqdm
from typing import List, Union
from math import ceil
import re
from elastic_wikidata.http import generate_user_agent
from elastic_wikidata.config import runtime_config


class get_entities:
    def __init__(self):
        """
        One instance of this class per list of qcodes. The JSON response for a list of qcodes is made to Wikidata on 
        creation of a class instance. 

        Args:
            qcodes (str/list): Wikidata qcode or list of qcodes/
            lang (str, optional): Defaults to 'en'.
            page_limit (int): page limit for Wikidata API. Usually 50, can reach 500. 
        """
        self.endpoint = (
            "http://www.wikidata.org/w/api.php?action=wbgetentities&format=json"
        )

        self.properties = ["labels", "aliases", "claims", "descriptions"]

    @staticmethod
    def _param_join(params: List[str]) -> str:
        """
        Joins list of parameters for the URL. ['a', 'b'] -> "a%7Cb"

        Args:
            params (list): list of parameters (strings)

        Returns:
            str
        """

        return "%7C".join(params) if len(params) > 1 else params[0]

    @classmethod
    def get_all_results(
        self, qcodes, lang="en", page_limit=50, timeout: int = None
    ) -> list:
        """
        Get response through the `wbgetentities` API. 

        Returns:
            list: each item is a the response for an entity
        """

        results = self().result_generator(qcodes, lang, page_limit, timeout)

        all_results = []

        print(f"Getting {len(qcodes)} wikidata documents in pages of {page_limit}")

        for res in tqdm(results, total=ceil(len(qcodes) / page_limit)):
            all_results += res

        return all_results

    @classmethod
    def result_generator(
        self, qcodes, lang="en", page_limit=50, timeout: int = None
    ) -> list:
        """
        Get response through the `wbgetentities` API. Yields `page_limit` entities at a time.

        Returns:
            list: each item is a the response for an entity
        """

        if isinstance(qcodes, str):
            qcodes = [qcodes]

        qcodes_paginated = [
            qcodes[i : i + page_limit] for i in range(0, len(qcodes), page_limit)
        ]

        headers = {"User-Agent": generate_user_agent()}

        if timeout is None:
            timeout = runtime_config.get("http_timeout")

        with requests.Session() as s:
            for page in qcodes_paginated:
                url = f"http://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids={self._param_join(page)}&props={self._param_join(self().properties)}&languages={lang}&languagefallback=1&formatversion=2"
                response = s.get(url, headers=headers, timeout=timeout).json()
                yield [v for _, v in response["entities"].items()]

    def get_labels(self, qcodes, lang="en", page_limit=50, timeout: int = None) -> dict:
        """
        Get labels from Wikidata qcodes. If the item associated with a qcode has no label, its value
        in the dictionary is an empty string.

        Returns:
            dict: {qid1: label1, qid2: label2, ...}
        """

        qid_label_mapping = dict()
        qcodes = list(set(qcodes))

        docs = self.get_all_results(qcodes, lang, page_limit, timeout)

        for doc in docs:
            qid_label_mapping[doc["id"]] = doc["labels"].get(lang, {}).get("value", "")

        return qid_label_mapping


def simplify_wbgetentities_result(
    doc: Union[dict, List[dict]],
    lang: str,
    properties: list,
    use_redirected_qid: bool = False,
) -> Union[dict, List[dict]]:
    """
    Processes a single document or set of documents from the JSON result of wbgetentities, returning a simplified version of that document. 

    Args:
        doc (Union[dict, List[dict]]): JSON result from Wikidata wbgetentities API
        lang (str): Wikimedia language code
        properties (list): list of Wikidata properties
        use_redirected_qid (bool, optional): whether to return the redirected QID value under the 'id' field instead of the original QID 
            if there is one. Defaults to False.

    Returns:
        Union[dict, List[dict]]: dict if single record passed in; list if multiple records
    """

    # if list of dicts, run this function for each dict
    if isinstance(doc, list) and isinstance(doc[0], dict):
        return [simplify_wbgetentities_result(item, lang, properties) for item in doc]

    wd_type_mapping = {
        "wikibase-entityid": "id",
        "time": "time",
        "monolingualtext": "text",
        "quantity": "amount",
    }

    # check for redirected URL
    if "redirects" in doc:
        if use_redirected_qid:
            newdoc = {"id": doc["redirects"]["to"]}
        else:
            newdoc = {"id": doc["redirects"]["from"]}

    else:
        newdoc = {"id": doc["id"]}

    # add label(s)
    if lang in doc.get("labels", {}):
        newdoc["labels"] = doc["labels"][lang]["value"]

    # add descriptions(s)
    if lang in doc.get("descriptions", {}):
        newdoc["descriptions"] = doc["descriptions"][lang]["value"]

    # add aliases
    if (len(doc.get("aliases", {})) > 0) and (lang in doc.get("aliases", {})):
        newdoc["aliases"] = [i["value"] for i in doc["aliases"][lang]]
    else:
        newdoc["aliases"] = []

    # add claims (property values)
    newdoc["claims"] = {}

    if "claims" in doc:
        for p in properties:
            if p in doc["claims"]:
                claims = []
                for i in doc["claims"][p]:
                    try:
                        value_type = i["mainsnak"]["datavalue"]["type"]
                        if value_type == "string":
                            claims.append(i["mainsnak"]["datavalue"]["value"])
                        else:
                            value_name = wd_type_mapping[value_type]
                            claims.append(
                                i["mainsnak"]["datavalue"]["value"][value_name]
                            )
                    except KeyError:
                        pass

                newdoc["claims"][p] = claims

    return newdoc


def wiki_property_check(p):
    if len(re.findall(r"(p\d+)", p.lower())) == 1:
        return True
    else:
        print(f"WARNING: property {p} is not a valid Wikidata property")
        return False

import requests
from tqdm.auto import tqdm
from typing import List, Union
from math import ceil


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
    def get_all_results(self, qcodes, lang="en", page_limit=50) -> list:
        """
        Get response through the `wbgetentities` API. 

        Returns:
            list: each item is a the response for an entity
        """

        results = self().result_generator(qcodes, lang, page_limit)

        all_results = []

        print(f"Getting {len(qcodes)} wikidata documents in pages of {page_limit}")

        for res in tqdm(results, total=ceil(len(qcodes) / page_limit)):
            all_results += res

        return all_results

    @classmethod
    def result_generator(self, qcodes, lang="en", page_limit=50) -> list:
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

        for page in qcodes_paginated:
            url = f"http://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids={self._param_join(page)}&props={self._param_join(self().properties)}&languages={lang}&languagefallback=1&formatversion=2"
            response = requests.get(url).json()
            yield [v for _, v in response["entities"].items()]

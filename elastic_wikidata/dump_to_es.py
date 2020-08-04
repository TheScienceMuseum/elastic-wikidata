import json
from itertools import islice
from tqdm.auto import tqdm
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from typing import Union
import re
from elastic_wikidata.wd_entities import get_entities


class processDump:
    def __init__(
        self, dump: Union[str, list], es_credentials: dict, index_name: str, **kwargs
    ):
        self.config = {
            "chunk_size": 1000,
            "queue_size": 8,
            "lang": "en",
            "properties": ["P31"],
        }

        self.es_credentials = es_credentials

        if isinstance(dump, str):
            self.dump_path = dump
            self.entities = None
        elif isinstance(dump, list):
            self.entities = dump
            self.dump_path = None
        else:
            raise ValueError(
                "dump must either be path to JSON dump or Python list of entitiess"
            )

        self.index_name = index_name

        # process kwargs/set defaults
        if "doc_limit" in kwargs:
            self.doc_limit = kwargs["doc_limit"]
        else:
            self.doc_limit = None

        self.wiki_options = {}

        if "lang" in kwargs:
            self.wiki_options["lang"] = kwargs["lang"]
        else:
            self.wiki_options["lang"] = "en"

        def wiki_property_check(p):
            if len(re.findall(r"(p\d+)", p.lower())) == 1:
                return True
            else:
                print(f"WARNING: property {p} is not a valid Wikidata property")
                return False

        if "properties" in kwargs:
            if isinstance(kwargs["properties"], str) and wiki_property_check(
                kwargs["properties"]
            ):
                self.wiki_options["properties"] = [
                    kwargs["properties"].upper()
                ]  # [P31], not [p31]
            elif isinstance(kwargs["properties"], list):
                self.wiki_options["properties"] = [
                    item.upper()
                    for item in kwargs["properties"]
                    if wiki_property_check(item)
                ]
        else:
            self.wiki_options["properties"] = ["P31"]

    def start_elasticsearch(self):
        """
        Creates an Elasticsearch index. If SEARCH_CLUSTER, ELASTICSEARCH_USER & ELASTICSEARCH_PASSWORD
        are specified in config it uses those, otherwise uses a locally running Elasticsearch instance.
        """

        if "ELASTICSEARCH_CLUSTER" in self.es_credentials:
            print(
                f"Connecting to Elasticsearch at {self.es_credentials['ELASTICSEARCH_CLUSTER']}"
            )
            self.es = Elasticsearch(
                [self.es_credentials["ELASTICSEARCH_CLUSTER"]],
                http_auth=(
                    self.es_credentials["ELASTICSEARCH_USER"],
                    self.es_credentials["ELASTICSEARCH_PASSWORD"],
                ),
            )
        else:
            # run on localhost
            print("Connecting to Elasticsearch on localhost")
            self.es = Elasticsearch()

        self.es.indices.create(index=self.index_name, ignore=400)

    def dump_to_es(self):
        print("Indexing documents...")
        successes = 0
        errors = []

        # if dump_path, use generator that passes
        if self.dump_path:
            action_generator = self.generate_actions_from_dump()
        elif self.entities:
            action_generator = self.generate_actions_from_entities()

        for ok, action in tqdm(
            parallel_bulk(
                client=self.es,
                index=self.index_name,
                actions=action_generator,
                chunk_size=self.config["chunk_size"],
                queue_size=self.config["queue_size"],
            ),
        ):
            if not ok:
                print(action)
                errors.append(action)
            successes += ok

    def process_doc(self, doc: dict) -> dict:
        """
        Processes a single document from the JSON dump, returning a filtered version of that document. 
        """

        lang = self.wiki_options["lang"]
        properties = self.wiki_options["properties"]

        newdoc = {"id": doc["id"]}

        # add label(s)
        if lang in doc["labels"]:
            newdoc["labels"] = doc["labels"][lang]["value"]

        # add descriptions(s)
        if lang in doc["descriptions"]:
            newdoc["descriptions"] = doc["descriptions"][lang]["value"]

        # add aliases
        if (len(doc["aliases"]) > 0) and (lang in doc["aliases"]):
            newdoc["aliases"] = [i["value"] for i in doc["aliases"][lang]]
        else:
            newdoc["aliases"] = []

        # add claims (property values)
        newdoc["claims"] = {}

        for p in properties:
            if p in doc["claims"]:
                newdoc["claims"][p] = [
                    i["mainsnak"]["datavalue"]["value"]["id"] for i in doc["claims"][p]
                ]

        return newdoc

    def generate_actions_from_dump(self):
        """
        Generator to yield a processed document from the Wikidata JSON dump. 
        Each line of the Wikidata JSON dump is a separate document. 
        """
        with open(self.dump_path) as f:
            objects = (json.loads(line) for line in f)

            # optionally limit number that are loaded
            if self.doc_limit is not None:
                objects = islice(objects, self.doc_limit)

            for item in objects:
                doc = self.process_doc(item)

                yield doc

    def generate_actions_from_entities(self):
        """
        Generator to yield processed document from list of entities. Calls are made to 
        wbgetentities API with page size of 50 to retrieve documents.
        """

        json_generator = get_entities.result_generator(
            self.entities, lang=self.wiki_options["lang"]
        )

        for page in json_generator:
            for item in page:
                yield self.process_doc(item)

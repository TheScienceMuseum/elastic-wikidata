import json
from itertools import islice
from tqdm.auto import tqdm
from elasticsearch import Elasticsearch
from elasticsearch.helpers import parallel_bulk
from elastic_wikidata.config import config


class processDump:
    def __init__(self, dump_path: str, index_name: str, **kwargs):
        self.config = {
            "chunk_size": 1000,
            "queue_size": 8,
            "lang": "en",
            "properties": ["P31"],
        }

        self.dump_path = dump_path
        self.index_name = index_name

        if "doc_limit" in kwargs:
            self.doc_limit = kwargs["doc_limit"]
        else:
            self.doc_limit = None

    def start_elasticsearch(self):
        """
        Creates an Elasticsearch index. If SEARCH_CLUSTER, ELASTICSEARCH_USER & ELASTICSEARCH_PASSWORD
        are specified in config it uses those, otherwise uses a locally running Elasticsearch instance.
        """

        if hasattr(config, "ELASTIC_SEARCH_CLUSTER"):
            print(f"Connecting to Elasticsearch at {config.ELASTICSEARCH_CLUSTER}")
            self.es = Elasticsearch(
                [config.ELASTICSEARCH_CLUSTER],
                http_auth=(config.ELASTICSEARCH_USER, config.ELASTICSEARCH_PASSWORD),
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
        for ok, action in tqdm(
            parallel_bulk(
                client=self.es,
                index=self.index_name,
                actions=self.generate_actions(),
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

        lang = self.config["lang"]

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

        for p in self.config["properties"]:
            if p in doc["claims"]:
                newdoc["claims"][p] = [
                    i["mainsnak"]["datavalue"]["value"]["id"] for i in doc["claims"][p]
                ]

        return newdoc

    def generate_actions(self):
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

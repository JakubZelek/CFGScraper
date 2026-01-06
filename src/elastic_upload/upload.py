import asyncio
import json
import hashlib
import logging
from common.managers.kafka import KafkaConsumerManager
from common.managers.elastic import ElasticSearchManager
from common.core.config import ElasticUploadSettings

elastic_upload_settings = ElasticUploadSettings()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

def yield_single_graph_to_be_loaded_to_elasticsearch(cfg_message :str):
    global_template = {
        "filepath": cfg_message["filepath"].replace("/repos/", ""),
        "commit_hash": cfg_message["commit_hash"],
        "repo_url": cfg_message["repo_url"],
        "language": cfg_message["language"],
    }

    for graph in cfg_message["graph_list"]:
        to_hash = graph["name"] + global_template["repo_url"] + global_template["commit_hash"]
        graph_id = hashlib.md5(to_hash.encode("utf-8")).hexdigest()

        yield graph_id, {**global_template, **graph}

async def upload_to_elasticsearch():
    elastic_manager = ElasticSearchManager(hostname=elastic_upload_settings.elastic_host)
    kafka_consumer = KafkaConsumerManager(kafka_topic=elastic_upload_settings.kafka_topic, kafka_broker=elastic_upload_settings.kafka_broker)

    for message in kafka_consumer.get_messages():
        for graph_id, graph_data in yield_single_graph_to_be_loaded_to_elasticsearch(message):

            graph_data["graph_dict"] = json.dumps(graph_data["graph_dict"])
            found_isomorphism = await elastic_manager.get_isomorphic_graph_id(
                graph=graph_data,
                index=elastic_upload_settings.cfg_index
            )

            if found_isomorphism:
                isomorphism_data = {
                    "isomorphic_to": found_isomorphism,
                    "filepath": graph_data["filepath"],
                    "commit_hash": graph_data["commit_hash"],
                    "repo_url": graph_data["repo_url"],
                    "language": graph_data["language"],
                    "name": graph_data["name"],
                }
                await elastic_manager.insert_document(elastic_upload_settings.isomorphism_index, graph_id, isomorphism_data)
            else:
                await elastic_manager.insert_document(elastic_upload_settings.cfg_index, graph_id, graph_data)

if __name__ == "__main__":
    asyncio.run(upload_to_elasticsearch())

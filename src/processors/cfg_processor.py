import asyncio
import logging
import traceback
from datetime import datetime, timezone
from common.managers.kafka import KafkaConsumerManager, KafkaProducerManager
from common.managers.repository import RepositoryManager
from common.managers.elastic import ElasticSearchManager
from common.models import GraphBatch
from common.core.config import CfgProcessorSettings
from common.models import Graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

cfg_processor_settings = CfgProcessorSettings()

async def cfg_processor():
    kafka_consumer = KafkaConsumerManager(
        kafka_topic=cfg_processor_settings.language, kafka_broker=cfg_processor_settings.kafka_broker
    )
    kafka_producer = KafkaProducerManager(kafka_broker=cfg_processor_settings.kafka_broker)
    elastic_manager = ElasticSearchManager(hostname=cfg_processor_settings.elastic_host)

    logger.info(f"CFG Processor started, listening on topic: {cfg_processor_settings.language}")

    for message in kafka_consumer.get_messages():
        logger.info(f"Processing message: {message}")

        url = message["url"]
        repo_path = f"/repos/{url.split('/')[-1]}"
        repository_manager = RepositoryManager(url)

        try:

            logger.info(f"Clone repository: {message['url']}")
            repository_manager.clone_and_build(cfg_processor_settings.repo_script)

            commit_hash = repository_manager.get_commit_hash(repo_path=repo_path)

            for filename in repository_manager.get_files(extension=cfg_processor_settings.extention, folder="/repos"):
                logger.info(f"Processing file: {filename}")
                control_flow_graphs = repository_manager.generate_cfg_from_file(
                    filename, cfg_build_script=cfg_processor_settings.cfg_build_script
                )
                logger.info(f"Control flow graphs: {control_flow_graphs}")
                graph_list = [Graph(name=g["name"], graph_dict=g["graph_dict"], other_graph_info=g.get("other_graph_info")) for g in control_flow_graphs["graphs"]]
                
                graph_batch = GraphBatch(filepath=str(filename), commit_hash=commit_hash, repo_url=url, language=cfg_processor_settings.language, graph_list=graph_list)
                kafka_producer.push_to_the_topic(cfg_processor_settings.graph_kafka_topic, graph_batch.model_dump())

            kafka_producer.flush()
            
            logger.info(f"Remove repository: {repo_path}")
            repository_manager.rm(repo_path)
            
            logger.info(f"Finished processing: {message['url']}")

        except Exception as e:
            logger.error(f"Failed to process {url}: {e}")
            error_doc = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": "cfg_processor",
                "repo_url": url,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
            await elastic_manager.insert_document(
                cfg_processor_settings.error_index,
                f"{url}_{datetime.now(timezone.utc).timestamp()}",
                error_doc
            )
            continue

asyncio.run(cfg_processor())
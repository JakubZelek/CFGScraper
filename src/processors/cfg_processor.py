import logging
from common.managers.kafka import KafkaConsumerManager, KafkaProducerManager
from common.managers.repository import RepositoryManager
from common.models import GraphBatch
from common.core.config import CfgProcessorSettings
from common.models import Graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

cfg_processor_settings = CfgProcessorSettings()

def cfg_processor():
    kafka_consumer = KafkaConsumerManager(
        kafka_topic=cfg_processor_settings.language, kafka_broker=cfg_processor_settings.kafka_broker
    )
    kafka_producer = KafkaProducerManager(kafka_broker=cfg_processor_settings.kafka_broker)

    logger.info(f"CFG Processor started, listening on topic: {cfg_processor_settings.language}")

    for message in kafka_consumer.get_messages():
        logger.info(f"Processing message: {message}")

        url = message["url"]
        repo_path = f"/repos/{url.split('/')[-1]}"
        repository_manager = RepositoryManager(url)
        repository_manager.clone_and_build(cfg_processor_settings.repo_script)

        commit_hash = repository_manager.get_commit_hash(repo_path=repo_path)

        for filename in repository_manager.get_files(extension=cfg_processor_settings.extention, folder="/repos"):
            logger.info(f"Processing file: {filename}")
            control_flow_graphs = repository_manager.generate_cfg_from_file(
                filename, cfg_build_script=cfg_processor_settings.cfg_build_script
            )
            control_flow_graphs["commit_hash"] = commit_hash
            control_flow_graphs["filepath"] = str(filename)
            control_flow_graphs["repo_url"] = url
            control_flow_graphs["language"] = cfg_processor_settings.language
            graph_list = [Graph(name=g["name"], graph_dict=g["graph"], other_graph_info=None) for g in control_flow_graphs["graphs"]]
            logger.info(f"Graphs generated : {control_flow_graphs}")
            
            graph_batch = GraphBatch(filepath=str(filename), commit_hash=commit_hash, repo_url=url, language=cfg_processor_settings.language, graph_list=graph_list)
            kafka_producer.push_to_the_topic(cfg_processor_settings.graph_kafka_topic, graph_batch.model_dump())

        kafka_producer.flush()
        repository_manager.rm(repo_path)
        logger.info(f"Finished processing: {message['url']}")

cfg_processor()
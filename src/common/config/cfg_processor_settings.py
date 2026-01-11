from pydantic_settings import BaseSettings

class CfgProcessorSettings(BaseSettings):
    language: str
    extension: str
    kafka_broker: str
    graph_kafka_topic: str
    language_topics: str
    repo_script: str
    cfg_build_script: str
    elastic_host: str
    error_index: str
    repo_folder: str
    logging_to_elastics: bool = True

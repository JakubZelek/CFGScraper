from pydantic_settings import BaseSettings

class ElasticUploadSettings(BaseSettings):
    kafka_broker: str
    cfg_isomorphism_index: str
    cfg_index: str
    error_index: str
    graph_kafka_topic: str
    elastic_host: str

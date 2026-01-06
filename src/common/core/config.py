from pydantic_settings import BaseSettings


class UrlAppSettings(BaseSettings):
    kafka_host: str
    kafka_topic: str
    elastic_host: str
    elastic_index: str
    language_topics: str
    app_name: str
    debug: bool = False

    def language_topics_list(self) -> list[str]:
        return self.language_topics.split(",")


class CfgProcessorSettings(BaseSettings):
    language: str
    extention: str
    kafka_broker: str
    graph_kafka_topic: str
    language_topics: str
    repo_script: str
    cfg_build_script: str


class ElasticUploadSettings(BaseSettings):
    kafka_broker: str
    isomorphism_index: str
    cfg_index: str
    kafka_topic: str
    elastic_host: str
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

settings = UrlAppSettings()

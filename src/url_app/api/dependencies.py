from common.core.config import UrlAppSettings
from common.managers.kafka import KafkaProducerManager
from common.managers.elastic import ElasticSearchManager
from common.services.process_url import ProcessUrlService

url_app_settings = UrlAppSettings()

kafka_manager = KafkaProducerManager(url_app_settings.kafka_host)
elastic_manager = ElasticSearchManager(url_app_settings.elastic_host)
event_service = ProcessUrlService(elastic_manager, kafka_manager, url_app_settings)

def get_event_service() -> ProcessUrlService:
    return event_service

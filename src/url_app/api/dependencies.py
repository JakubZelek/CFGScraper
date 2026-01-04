from common.core.config import settings
from common.managers.kafka import KafkaProducerManager
from common.managers.elastic import ElasticSearchManager
from common.services.process_url import ProcessUrlService

kafka_manager = KafkaProducerManager(settings.kafka_host)
elastic_manager = ElasticSearchManager(settings.elastic_host)
event_service = ProcessUrlService(elastic_manager, kafka_manager, settings.elastic_index)

def get_event_service() -> ProcessUrlService:
    return event_service

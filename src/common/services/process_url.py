
from common.schemas.url_app import RepoUrl, RepoUrlList
from common.managers.elastic import ElasticSearchManager
from common.managers.kafka import KafkaProducerManager
from common.core.config import settings

class ProcessUrlService:
    def __init__(self, elastic_manager: ElasticSearchManager, kafka_manager: KafkaProducerManager, elastic_repository_index: str):
        self.kafka_manager = kafka_manager
        self.elastic_manager = elastic_manager
        self.elastic_repository_index = elastic_repository_index
        
    async def scrap_single_repo(self, repo_input: RepoUrl):
        if repo_input.language_topic not in settings.language_topics_list():
            return {"status": "topic not available"}
    
        if await self.elastic_manager.is_repo_in_the_index(self.elastic_repository_index, repo_input.url):
            return {"status": "repo already exists"}

        await self.kafka_manager.push_to_the_topic(topic=repo_input.language_topic, message=repo_input.model_dump())
        await self.elastic_manager.insert_repo_info(self.elastic_repository_index, repo_input.url)
        await self.kafka_manager.flush()
    
        return {"status": "repo processed"}
        

    async def scrap_multiple_repos(self, repo_input: RepoUrlList):
        if repo_input.language_topic not in settings.language_topics_list():
            return {"status": "topic not available"}
        
        repos_already_exists = []
        repos_processed = []
    
        for url in repo_input.url_list:
            if not await self.elastic_manager.is_repo_in_the_index(self.elastic_repository_index, url):            
                message = repo_input.model_dump()
                message["url"] = url
                message.pop("url_list")

                await self.kafka_manager.push_to_the_topic(topic=repo_input.language_topic, message=message)
                await self.elastic_manager.insert_repo_info(self.elastic_repository_index, url)
                repos_processed.append(url)
            else:
                repos_already_exists.append(url)

        await self.kafka_manager.flush()
        return {"status": {"repos_processed": repos_processed, "repos_already_exists": repos_already_exists}}
import json
import networkx as nx
from networkx.algorithms import isomorphism
from elasticsearch import AsyncElasticsearch
from common.elastic_queries.queries import check_isomorphism_query


class ElasticSearchManager:
    def __init__(self, hostname: str):
        self.elasticsearch = AsyncElasticsearch(hosts=[hostname])

    async def index_exists(self, index: str):
        return await self.elasticsearch.indices.exists(index=index)

    async def create_index(self, index: str):
        await self.elasticsearch.indices.create(index=index)
    
    async def is_repo_in_the_index(self, index: str, repo_url: str):
        return await self.elasticsearch.exists(index=index, id=repo_url)

    async def insert_repo_info(self, index: str, repo_url: str):
        await self.elasticsearch.index(index=index, id=repo_url, document={})

    async def delete_repo_info(self, index: str, repo_url: str):
        await self.elasticsearch.delete(index=index, id=repo_url)

    async def get_isomorphic_graph_id(
        self, graph: nx.Graph, index: str, scroll_size: int = 10000
    ) -> str | None:
        query = check_isomorphism_query(
            graph["num_edges"], graph["out_degrees"], graph["in_degrees"]
        )

        response = await self.elasticsearch.search(
            index=index, body=query, scroll="2m", size=scroll_size
        )
        scroll_id = response.get("_scroll_id")
        
        while len(response["hits"]["hits"]) > 0:
            for hit in response["hits"]["hits"]:
                candidate_data = json.loads(hit["_source"]["graph"])
                isomorphism_candidate = nx.DiGraph(candidate_data)

                matcher = isomorphism.DiGraphMatcher(graph, isomorphism_candidate)
                if matcher.is_isomorphic():
                    return hit["_id"]

            response = await self.elasticsearch.scroll(scroll_id=scroll_id, scroll="2m")

        return None

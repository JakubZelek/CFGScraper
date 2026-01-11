from typing import Optional
from pydantic import BaseModel, ValidationError, model_validator, field_validator


class Graph(BaseModel):
    name: str
    graph_dict: dict
    in_degrees: Optional[str] = None
    out_degrees: Optional[str] = None
    other_graph_info: Optional[dict] = None


    @field_validator("graph_dict", mode="before")
    @classmethod
    def validate_graph_dict(cls, graph):
        all_nodes = set(graph.keys())
        for targets in graph.values():
            for tgt in targets:
                if tgt not in all_nodes:
                    raise ValidationError(f"Node '{tgt}' is not defined as a key!")
        return graph

    @model_validator(mode="after")
    def fulfill_graph_based_field(self):
        """
        Computes out degrees of the nodes, sort them and returns as a string.
        """
        if self.out_degrees is None:
            self.out_degrees = str(
                sorted([len(neighbors) for neighbors in self.graph_dict.values()])
            )

        if self.in_degrees is None:
            degrees = {node: 0 for node in self.graph_dict}
            for neighbors in self.graph_dict.values():
                for neighbor in neighbors:
                    degrees[neighbor] = degrees.get(neighbor, 0) + 1
            self.in_degrees = str(sorted([degrees[node] for node in self.graph_dict]))        

        return self


class GraphBatch(BaseModel):
    filepath: str
    commit_hash: str
    repo_url: str
    language: str
    graph_list: list[Graph]

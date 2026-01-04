def check_isomorphism_query(num_edges: int, out_degrees: str, in_degrees: str):
    query = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"num_edges": num_edges}},
                    {"term": {"out_degrees.keyword": out_degrees}},
                    {"term": {"in_degrees.keyword": in_degrees}},
                ]
            }
        }
    }
    return query
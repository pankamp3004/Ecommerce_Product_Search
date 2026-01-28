from backend.search import hybrid_search
res = hybrid_search(
    query="shirts", 
    max_price=1000
)

for hit in res["hits"]["hits"]:
    print(f"title: {hit["_source"]["title"]}, Relevency Score: {hit["_score"]}, Selling Prize: {hit["_source"]['selling_price']}, MRP: {hit["_source"]["mrp"]}")

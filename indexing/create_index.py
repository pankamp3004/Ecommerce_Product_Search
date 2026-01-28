from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ELASTIC_USERNAME = "elastic"
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
INDEX_NAME = os.getenv("INDEX_NAME", "ecommerce_products_v1")

# Connect to Elasticsearch
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
    verify_certs=False  # local self-signed cert
)

# Test connection
if es.ping():
    print("Connected to Elasticsearch")
else:
    print("Elasticsearch connection failed")

# DELETE index if exists (IMPORTANT when changing mapping)
if es.indices.exists(index=INDEX_NAME):
    es.indices.delete(index=INDEX_NAME)
    print(f"Deleted existing index `{INDEX_NAME}`")

# Final index mapping (PRODUCTION-GRADE)
mapping = {
    "mappings": {
        "properties": {
            "product_id": {"type": "keyword"},

            # UI
            "image_url": {"type": "keyword"},
            "product_url": {"type": "keyword"},

            # BM25 Text Search
            "title": {
                "type": "text",
                "fields": {
                    "keyword": {"type": "keyword"}  # sorting / aggregations
                }
            },
            "product_details": {"type": "text"},

            # Filters (RAW)
            "brand": {"type": "keyword"},
            "category": {"type": "keyword"},
            "colour": {"type": "keyword"},

            # Filters (NORMALIZED for case-insensitive)
            "brand_normalized": {"type": "keyword"},
            "category_normalized": {"type": "keyword"},
            "colour_normalized": {"type": "keyword"},

            "size": {"type": "keyword"},
            "competitor": {"type": "keyword"},

            # Numeric fields
            "selling_price": {"type": "float"},
            "mrp": {"type": "float"},
            "star_rating": {"type": "float"},

            # Vector Search (MiniLM → 384 dims)
            "embedding": {
                "type": "dense_vector",
                "dims": 384,
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}

# Create index
es.indices.create(index=INDEX_NAME, body=mapping)
print(f"Index `{INDEX_NAME}` created successfully")






# from elasticsearch import Elasticsearch
# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# ELASTIC_USERNAME = "elastic"
# ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
# INDEX_NAME = os.getenv("INDEX_NAME", "ecommerce_products_v1")

# # Connect to Elasticsearch
# es = Elasticsearch(
#     "https://localhost:9200",
#     basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
#     verify_certs=False  # local self-signed cert
# )

# # Test connection
# if es.ping():
#     print("✅ Connected to Elasticsearch")
# else:
#     print("❌ Elasticsearch connection failed")

# # Final index mapping
# mapping = {
#     "mappings": {
#         "properties": {
#             "product_id": {"type": "keyword"},

#             # UI
#             "image_url": {"type": "keyword"},
#             "product_url": {"type": "keyword"},

#             # BM25 Text Search
#             "title": {
#                 "type": "text",
#                 "fields": {
#                     "keyword": {"type": "keyword"}  # sorting / aggregations
#                 }
#             },
#             "product_details": {"type": "text"},

#             # Filters
#             "brand": {"type": "keyword"},
#             "category": {"type": "keyword"},
#             "colour": {"type": "keyword"},
#             "size": {"type": "keyword"},
#             "competitor": {"type": "keyword"},

#             # Numeric fields
#             "selling_price": {"type": "float"},
#             "mrp": {"type": "float"},
#             "star_rating": {"type": "float"},

#             # Vector Search (MiniLM → 384 dims)
#             "embedding": {
#                 "type": "dense_vector",
#                 "dims": 384,
#                 "index": True,
#                 "similarity": "cosine"
#             }
#         }
#     }
# }

# # Create index safely
# if not es.indices.exists(index=INDEX_NAME):
#     es.indices.create(index=INDEX_NAME, body=mapping)
#     print(f"✅ Index `{INDEX_NAME}` created successfully")
# else:
#     print(f"⚠️ Index `{INDEX_NAME}` already exists")

from elasticsearch import Elasticsearch
from indexing.embeddings import embed_text
import os
import re
from dotenv import load_dotenv
from rapidfuzz import process, fuzz
from indexing.category_normalizer import CATEGORY_MAP

load_dotenv()

ELASTIC_USERNAME = "elastic"
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
    verify_certs=False
)

INDEX_NAME = os.environ['INDEX_NAME']

# -----------------------------
# BRAND RESOLUTION (FUZZY)
# -----------------------------

KNOWN_BRANDS = [
    "nike", "adidas", "campus", "puma", "reebok", "skechers"
]

def resolve_brand_fuzzy(query: str, threshold: int = 80) -> str | None:
    match, score, _ = process.extractOne(
        query.lower(),
        KNOWN_BRANDS,
        scorer=fuzz.partial_ratio
    )
    if score >= threshold:
        return match
    return None


# -----------------------------
# CATEGORY RESOLUTION (QUERY INTENT)
# -----------------------------

# def resolve_category_from_query(query: str, threshold: int = 80) -> str | None:
#     q = query.lower()

#     best_category = None
#     best_score = 0

#     for canonical, variants in CATEGORY_MAP.items():
#         # Score canonical name
#         canonical_text = canonical.replace("_", " ")
#         score = fuzz.partial_ratio(q, canonical_text)

#         if score > best_score:
#             best_score = score
#             best_category = canonical

#         #Score all variants
#         for v in variants:
#             v_score = fuzz.partial_ratio(q, v.lower())

#             if v_score > best_score:
#                 best_score = v_score
#                 best_category = canonical

#     # Apply threshold
#     if best_score >= threshold:
#         return best_category

#     return None



# -----------------------------
# PRICE EXTRACTION
# -----------------------------

def extract_max_price(query: str) -> float | None:
    m = re.search(r'(under|below|less than|upto|up to)\s*₹?\s*(\d+)', query.lower())
    if m:
        return float(m.group(2))
    return None


def extract_min_price(query: str) -> float | None:
    m = re.search(r'(above|over|more than|greater than)\s*₹?\s*(\d+)', query.lower())
    if m:
        return float(m.group(2))
    return None


# -----------------------------
# CLEAN QUERY (REMOVE FILTER WORDS)
# -----------------------------

def clean_query(
    query: str,
    brand: str | None,
    # category: str | None,
    max_price: float | None,
    min_price: float | None
) -> str:
    q = query.lower()

    if brand:
        q = q.replace(brand.lower(), "")

    # if category:
    #     q = q.replace(category.lower(), "")

    if max_price:
        q = re.sub(
            r'(under|below|less than|upto|up to)\s*₹?\s*' + str(int(max_price)),
            '',
            q
        )

    if min_price:
        q = re.sub(
            r'(above|over|more than|greater than)\s*₹?\s*' + str(int(min_price)),
            '',
            q
        )

    GENDER_PHRASES = ["for men", "for women","for man","for woman","men","man","women","woman","mens","womens", "for me", "me", "for boys", 
                      "for girls", "for boy", "for girl", "boys", "girls", "boy", "girl", "for wedding", "for weddings", "wedding"]

    for phrase in GENDER_PHRASES:
        # word boundary safe replace
        q = re.sub(rf"\b{re.escape(phrase)}\b", "", q)


    return " ".join(q.split())


# -----------------------------
# HYBRID SEARCH (PRODUCTION)
# -----------------------------

def hybrid_search(
    query: str,
    max_price: float | None = None,
    min_price: float | None = None,
    brand: str | None = None,
    # category: str | None=None, 
    size: int = 10
):
    # -----------------------------
    # 1. Query Understanding
    # -----------------------------

    resolved_brand = brand.lower() if brand else resolve_brand_fuzzy(query)
    # resolved_category = category.lower() if category else resolve_category_from_query(query)

    resolved_max_price = max_price if max_price else extract_max_price(query)
    resolved_min_price = min_price if min_price else extract_min_price(query)

    cleaned_query = clean_query(
        query,
        resolved_brand,
        # resolved_category,
        resolved_max_price,
        resolved_min_price
    )

    print("🧠 Query Understanding")
    print("  Original Query:   ", query)
    print("  Resolved Brand:   ", resolved_brand)
    # print("  Resolved Category:", resolved_category)
    print("  Resolved Min ₹:   ", resolved_min_price)
    print("  Resolved Max ₹:   ", resolved_max_price)
    print("  Cleaned Query:    ", cleaned_query)

    # -----------------------------
    # 2. Embedding
    # -----------------------------

    query_vector = embed_text(cleaned_query)
    print(f"🔢 Vector dimension: {len(query_vector)}")

    # -----------------------------
    # 3. Strict Filters (BUSINESS LOGIC)
    # -----------------------------

    filters = []

    if resolved_min_price:
        filters.append({"range": {"selling_price": {"gte": resolved_min_price}}})

    if resolved_max_price:
        filters.append({"range": {"selling_price": {"lte": resolved_max_price}}})

    if resolved_brand:
        filters.append({"term": {"brand_normalized": resolved_brand}})

    # if resolved_category:
    #     filters.append({"term": {"category_normalized": resolved_category}})

    # -----------------------------
    # 4. Hybrid Query (BM25 + Vector)
    # -----------------------------

    body = {
        "size": size,
        "min_score": 2.0,
        "query": {
            "bool": {
                "filter": filters,
                "should": [
                    {
                        "multi_match": {
                            "query": cleaned_query,
                            "fields": ["title", "product_details"]
                        }
                    },
                    {
                        "knn": {
                            "field": "embedding",
                            "query_vector": query_vector,
                            "k": 200,
                            "num_candidates": 500,
                            # "boost": 2.0
                        }
                    }
                ]
                # Business filters (DO NOT affect score)
                
                # Semantic reranking
                
            }
        }
    }

    return es.search(index=INDEX_NAME, body=body)





# from elasticsearch import Elasticsearch
# from indexing.embeddings import embed_text
# import os
# import re
# from dotenv import load_dotenv
# from rapidfuzz import process, fuzz

# load_dotenv()

# ELASTIC_USERNAME = "elastic"
# ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")

# es = Elasticsearch(
#     "https://localhost:9200",
#     basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
#     verify_certs=False  # local self-signed cert
# )

# INDEX_NAME = os.environ['INDEX_NAME']

# # -----------------------------
# # BRAND RESOLUTION (FUZZY)
# # -----------------------------

# # TODO: ideally load from DB or ES at startup
# KNOWN_BRANDS = [
#     "nike", "adidas", "campus", "puma", "reebok", "skechers"
# ]

# def resolve_brand_fuzzy(query: str, threshold: int = 80) -> str | None:
#     match, score, _ = process.extractOne(
#         query.lower(),
#         KNOWN_BRANDS,
#         scorer=fuzz.partial_ratio
#     )
#     if score >= threshold:
#         return match
#     return None


# # -----------------------------
# # PRICE EXTRACTION
# # -----------------------------

# def extract_max_price(query: str) -> float | None:
#     # under 5000, below 5000, less than 5000, upto 5000
#     m = re.search(r'(under|below|less than|upto|up to)\s*₹?\s*(\d+)', query.lower())
#     if m:
#         return float(m.group(2))
#     return None


# # -----------------------------
# # CLEAN QUERY (REMOVE FILTER TEXT)
# # -----------------------------

# def clean_query(query: str, brand: str | None, max_price: float | None) -> str:
#     q = query.lower()

#     if brand:
#         q = q.replace(brand.lower(), "")

#     if max_price:
#         q = re.sub(
#             r'(under|below|less than|upto|up to)\s*₹?\s*' + str(int(max_price)),
#             '',
#             q
#         )

#     # remove extra spaces
#     return " ".join(q.split())


# # -----------------------------
# # HYBRID SEARCH
# # -----------------------------

# def hybrid_search(
#     query: str,
#     max_price: float | None = None,
#     brand: str | None = None,
#     size: int = 10
# ):
#     # -----------------------------
#     # 1. Query Understanding
#     # -----------------------------

#     # Resolve brand (from param OR fuzzy from query)
#     resolved_brand = brand.lower() if brand else resolve_brand_fuzzy(query)

#     # Extract price if not passed
#     resolved_price = max_price if max_price else extract_max_price(query)

#     # Clean query for semantic + keyword
#     cleaned_query = clean_query(query, resolved_brand, resolved_price)

#     print("🧠 Query Understanding:")
#     print("  Original Query:", query)
#     print("  Resolved Brand:", resolved_brand)
#     print("  Resolved Max Price:", resolved_price)
#     print("  Cleaned Query:", cleaned_query)

#     # -----------------------------
#     # 2. Embedding
#     # -----------------------------

#     query_vector = embed_text(cleaned_query)
#     print(f"🔢 Vector dimension: {len(query_vector)}")

#     # -----------------------------
#     # 3. Strict Filters
#     # -----------------------------

#     filters = []

#     if resolved_price:
#         filters.append({"range": {"selling_price": {"lte": resolved_price}}})

#     if resolved_brand:
#         filters.append({"term": {"brand_normalized": resolved_brand}})

#     # -----------------------------
#     # 4. Hybrid Query (PRODUCTION)
#     # -----------------------------

#     body = {
#         "size": size,
#         "query": {
#             "bool": {
#                 "filter": filters,
#                 "should": [
#                     {
#                         "multi_match": {
#                             "query": cleaned_query,
#                             "fields": ["title", "product_details"],
#                             "boost": 2
#                         }
#                     },
#                     {
#                         "knn": {
#                             "field": "embedding",
#                             "query_vector": query_vector,
#                             "k": 50,
#                             "num_candidates": 200
#                         }
#                     }
#                 ],
#                 "minimum_should_match": 1
#             }
#         }
#     }

#     return es.search(index=INDEX_NAME, body=body)







# from elasticsearch import Elasticsearch
# from indexing.embeddings import embed_text
# import os
# from dotenv import  load_dotenv

# load_dotenv()


# ELASTIC_USERNAME = "elastic"
# ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")

# es = Elasticsearch(
#     "https://localhost:9200",
#     basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
#     verify_certs=False  # local self-signed cert
# )

# INDEX_NAME = os.environ['INDEX_NAME']

# def hybrid_search(
#     query: str,
#     max_price: float | None = None,
#     brand: str | None = None, 
#     size: int=10
# ):
#     query_vector = embed_text(query)
#     print(f"vector dimenstion of user query: {len(query_vector)}")

#     filters = []
#     if max_price:
#         filters.append({"range": {"selling_price": {"lte": max_price}}})
#     if brand:
#         filters.append({"term": {"brand": brand}})

#     body = {
#         "size": size,
#         "min_score": 3.0,     # is score is km vale remove ho jaynge (it's a thresold value)
#         "query": {
#             "bool": {
#                 "must": [
#                     {
#                         "multi_match": {
#                             "query": query,
#                             "fields": ["title", "product_details"]
#                         }
#                     }
#                 ],
#                 "filter": filters,
#                 "should": [
#                     {
#                         "knn": {
#                             "field": "embedding",
#                             "query_vector": query_vector,
#                             "k": 20,
#                             "num_candidates": 100,    # Internal optimization: Check 100 approximate neighbors , Choose best 10 Higher (more accurate but slower.)
#                             #"boost": 2.0     # Vector similarity contributes 2x more to final score
#                         }
#                     }
#                 ]
#             }
#         }
#     }

#     return es.search(index=INDEX_NAME, body=body)






from elasticsearch import Elasticsearch
from db import get_pg_connection
from category_normalizer import normalize_category
from embeddings import embed_text
from preprocess import preprocess
import math
import os
from dotenv import load_dotenv


load_dotenv()

ELASTIC_USERNAME = "elastic"
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
TABLE_NAME=os.getenv('TABLE_NAME')
INDEX_NAME = os.environ['INDEX_NAME']


es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
    verify_certs=False  # local self-signed cert
)


conn = get_pg_connection()
cur = conn.cursor()

cur.execute("""
    SELECT
        product_id,
        title,
        product_details,
        brand,
        category,
        colour,
        size,
        competitor,
        selling_price,
        mrp,
        star_rating,
        image_url,
        product_url
    FROM {TABLE_NAME}
""")

rows = cur.fetchall()


def safe(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    return v



for row in rows:
    (
        product_id, title, product_details, brand, category, colour,
        size, competitor, selling_price, mrp, star_rating,
        image_url, product_url
    ) = row

    # CLEAN embedding text (NO BRAND — brand is a FILTER, not semantic)
    embedding_text = preprocess(
        f"{safe(title)} {safe(product_details)} "
        f"Category {safe(normalize_category(category))}. "
        f"Colour {safe(colour)}"
    )

    doc = {
        "product_id": product_id,

        "title": safe(title),
        "product_details": safe(product_details),

        # Raw fields (UI / display)
        "brand": safe(brand),
        "category": safe(category),
        "colour": safe(colour),

        # Normalized fields (FILTERS)
        "brand_normalized": safe(brand.lower()) if brand else None,
        "category_normalized": safe(normalize_category(category)),
        "colour_normalized": safe(colour.lower()) if colour else None,

        "size": safe(size),
        "competitor": safe(competitor),

        "selling_price": safe(selling_price),
        "mrp": safe(mrp),
        "star_rating": safe(star_rating),

        "image_url": safe(image_url),
        "product_url": safe(product_url),

        "embedding": embed_text(embedding_text)
    }

    es.index(index=INDEX_NAME, id=product_id, document=doc)

print("Indexing completed successfully")




# from elasticsearch import Elasticsearch
# from db import get_pg_connection
# from embeddings import embed_text
# from preprocess import preprocess
# import math
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

# conn = get_pg_connection()
# cur = conn.cursor()

# cur.execute("""
#     SELECT
#         product_id,
#         title,
#         product_details,
#         brand,
#         category,
#         colour,
#         size,
#         competitor,
#         selling_price,
#         mrp,
#         star_rating,
#         image_url,
#         product_url
#     FROM ecommerce_products_mini
# """)

# rows = cur.fetchall()


# def safe(v):
#     if v is None:
#         return None
#     if isinstance(v, float) and math.isnan(v):
#         return None
#     return v


# for row in rows:
#     (
#         product_id, title, product_details, brand, category, colour,
#         size, competitor, selling_price, mrp, star_rating,
#         image_url, product_url
#     ) = row

#     embedding_text = preprocess(
#         f"{safe(title)} {safe(product_details)} "
#         f"Brand {safe(brand)} Category {safe(category)} Colour {safe(colour)}"
#     )

#     doc = {
#         "product_id": product_id,

#         "title": safe(title),
#         "product_details": safe(product_details),

#         "brand": safe(brand),
#         "category": safe(category),
#         "colour": safe(colour),
#         "size": safe(size),
#         "competitor": safe(competitor),

#         "selling_price": safe(selling_price),
#         "mrp": safe(mrp),
#         "star_rating": safe(star_rating),

#         "image_url": safe(image_url),
#         "product_url": safe(product_url),

#         "embedding": embed_text(embedding_text)
#     }

#     es.index(index=INDEX_NAME, id=product_id, document=doc)

# print("✅ Indexing completed")




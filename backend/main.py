from fastapi import FastAPI, Query, Request
import time
from typing import Optional, List
from backend.search import hybrid_search


app = FastAPI(
    title="E-commerce Hybrid Search API",
    description="BM25 + Vector Hybrid Search for E-commerce"
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000  # ms

    response.headers["X-Process-Time-ms"] = f"{process_time:.2f}"
    print(f"[API LATENCY] {request.url.path} = {process_time:.2f} ms")

    return response



@app.get("/")
def health_check():
    return {"status": "ok", "service": "ecommerce-search"}


@app.get("/search")
def search_products(
    q: str = Query(..., description="User search query"),
    max_price: Optional[float] = Query(None, description="Maximum selling price"),
    min_price: Optional[float] = Query(None, description="minimum selling price"),

    brand: Optional[str] = Query(None, description="Brand filter"),
    # category: Optional[str]=Query(None, descpiption="Category filter"), 
    size: int = Query(10, ge=1, le=50, description="Number of results to return")
):
    """
    Hybrid search endpoint:
    - q: user query text
    - max_price: optional price filter
    - min_price: optional price filter
    - brand: optional brand filter
    - size: number of results
    """

    # Call your hybrid search
    res = hybrid_search(
        query=q,
        max_price=max_price,
        min_price=min_price,
        brand=brand, 
        # category=category, 
        size=size
    )
    print(f"[ES LATENCY] took = {res['took']} ms")


    hits = res.get("hits", {}).get("hits", [])

    # Format response for frontend
    results = []
    for hit in hits[:size]:
        src = hit.get("_source", {})
        results.append({
            # "product_id": src.get("product_id"),
            "title": src.get("title"),
            "brand": src.get("brand"),
            "category": src.get("category"),
            "colour": src.get("colour"),
            "selling_price": src.get("selling_price"),
            "star_rating": src.get("star_rating"),
            # "image_url": src.get("image_url"),
            # "product_url": src.get("product_url"),
            "score": hit.get("_score")
        })

    return {
        "query": q,
        "filters": {
            "max_price": max_price,
            "min_price": min_price,
            "brand": brand
        },
        "count": len(results),
        "results": results
    }

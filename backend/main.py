from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
from typing import Optional, List
from backend.search import hybrid_search
from backend.chatbot import chat_graph
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI(
    title="E-commerce Hybrid Search API & Chatbot",
    description="BM25 + Vector Hybrid Search and AI Chatbot for E-commerce"
)

# Allow requests from the Next.js frontend (localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development; change to ["http://localhost:3000"] in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
def search_products_ep(
    q: str = Query(..., description="User search query"),
    max_price: Optional[float] = Query(None, description="Maximum selling price"),
    min_price: Optional[float] = Query(None, description="minimum selling price"),
    brand: Optional[str] = Query(None, description="Brand filter"),
    size: int = Query(10, ge=1, le=50, description="Number of results to return")
):
    """
    Hybrid search endpoint:
    """
    try:
        res = hybrid_search(
            query=q,
            max_price=max_price,
            min_price=min_price,
            brand=brand, 
            size=size
        )
        print(f"[ES LATENCY] took = {res.get('took', 0)} ms")
        
        hits = res.get("hits", {}).get("hits", [])
        results = []
        for hit in hits[:size]:
            src = hit.get("_source", {})
            results.append({
                "title": src.get("title"),
                "brand": src.get("brand"),
                "category": src.get("category"),
                "colour": src.get("colour"),
                "selling_price": src.get("selling_price"),
                "star_rating": src.get("star_rating"),
                "score": hit.get("_score")
            })

        return {
            "query": q,
            "filters": {"max_price": max_price, "min_price": min_price, "brand": brand},
            "count": len(results),
            "results": results
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

# ---- CHATBOT ENDPOINT ----

class MessageInput(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    messages: List[MessageInput]

@app.post("/chat")
def chat_endpoint(req: ChatRequest):
    """
    Conversational endpoint that uses LangGraph and OpenAI to answer queries using tool calling.
    """
    # Convert dicts to LangChain message classes
    lc_messages = []
    for m in req.messages:
        if m.role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            lc_messages.append(AIMessage(content=m.content))
            
    # Invoke the agent with the message history
    try:
        response = chat_graph.invoke({"messages": lc_messages})
        # The last message in the list is the final AI response
        last_message = response["messages"][-1]
        
        return {
            "role": "assistant",
            "content": last_message.content
        }
    except Exception as e:
        print(f"Agent error: {e}")
        return {
            "role": "assistant",
            "content": f"I'm sorry, I encountered an error: {str(e)}"
        }

# Triggering reload


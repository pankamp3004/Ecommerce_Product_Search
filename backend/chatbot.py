from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from backend.search import hybrid_search
from dotenv import load_dotenv

load_dotenv()

# Define the search tool for the AI
@tool
def search_products(query: str, max_price: float = None, min_price: float = None, brand: str = None, size: int = 5):
    """
    Search for e-commerce products in the catalog using hybrid search (Keyword + Semantic).
    Always use this tool when the user asks for recommendations, products, or questions about what is available.
    """
    try:
        # Call the actual search function
        results = hybrid_search(
            query=query,
            max_price=max_price,
            min_price=min_price,
            brand=brand,
            size=size
        )
        
        # Extract and format the hits
        hits = results.get("hits", {}).get("hits", [])
        if not hits:
            return "No products found matching those criteria."
            
        formatted_results = []
        for hit in hits:
            src = hit.get("_source", {})
            title = src.get("title", "Unknown Product")
            price = src.get("selling_price", "N/A")
            prod_brand = src.get("brand", "Unknown Brand")
            formatted_results.append(f"- {title} | Brand: {prod_brand} | Price: Rs. {price}")
            
        return "\n".join(formatted_results)
        
    except Exception as e:
        print(f"[TOOL EXCEPTION] Failed running search: {e}")
        import traceback
        traceback.print_exc()
        return f"Error executing search: {str(e)}"

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Create the LangGraph tool-calling ReAct agent
tools = [search_products]

system_prompt = """You are a helpful and polite virtual shopping assistant.
Your goal is to help users find products from the catalog. Uses the search_products tool extensively.
When you find products using the tool, present them clearly to the user.
If the tool returns no products, apologize and suggest they change their filters (like increasing the max price).
If the user asks a general question, you can answer it cheerfully.
"""

chat_graph = create_react_agent(llm, tools=tools, prompt=system_prompt)

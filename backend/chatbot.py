# i am using langgraph for my chatbot: 
# idea ..> consider hybrid search fun as a tool

from langchain_cerebras import ChatCerebras
from langgraph.graph import StateGraph, END, START
from typing import List, TypedDict

from dotenv import load_dotenv

load_dotenv()

llm = ChatCerebras(model="llama-3.3-70b")

class ChatState(TypedDict):
    user_id: str
    messages: List[dict]


def chatbot_node(state: ChatState):
    messages = state["messages"]

    response = llm.invoke(messages)

    messages.append({"role": "assistant", "content": response.content})

    return {"messages": messages}


workflow = StateGraph(ChatState)

workflow.add_node("chatbot", chatbot_node)

workflow.set_entry_point("chatbot")

workflow.add_edge("chatbot", END)

chat_graph = workflow.compile()

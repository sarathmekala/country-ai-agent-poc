import asyncio
import time
from fastapi import FastAPI, Body
from contextlib import asynccontextmanager

from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
# For history handling
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

app_state = {}

def convert_messages(openai_messages):
    """Converts OpenAI format to LangChain message objects."""
    history = []
    # Skip the last message as it's the current input
    for msg in openai_messages[:-1]:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history.append(AIMessage(content=msg["content"]))
    return history

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Initializing Warm MCP Connection (SSE)...")
    
    # Pointing to Port 8001 to avoid conflict with this FastAPI server on 8000
    client = MultiServerMCPClient({
        "rest_countries": {
            "url": "http://127.0.0.1:8001/sse", 
            "transport": "sse",
        }
    })
    
    try:
        tools = await client.get_tools()
        model = ChatOllama(model="qwen2.5:14b", temperature=0)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a precise geography assistant. Use tools only if data is missing from history. Respond only in English. Do not use other languages in your thought process or output."),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(model, tools, prompt)
        app_state["executor"] = AgentExecutor(agent=agent, tools=tools, verbose=True)
        app_state["client"] = client
        print("✅ System Ready.")
    except Exception as e:
        print(f"❌ Failed to connect to MCP: {e}")
    
    yield
    await client.close()

app = FastAPI(lifespan=lifespan)

@app.post("/v1/chat/completions")
async def openai_compat_chat(payload: dict = Body(...)):
    messages = payload.get("messages", [])
    user_input = messages[-1]["content"] if messages else ""
    
    # Routing logic
    # 1. SHARPER IDENTIFICATION
    # Check for Open WebUI's specific prompt headers
    is_background_task = any(trigger in user_input for trigger in [
        "### Task:", 
        "Generate a concise", 
        "Generate 1-3 broad tags",
        "suggest follow-up"
    ]) or "json" in user_input.lower() and "title" in user_input.lower()

    if is_background_task:
        print("⚡ Background Task")
        model = ChatOllama(model="qwen2.5:7b", temperature=0.7)
        response = await model.ainvoke(messages)
        content = response.content
    else:
        print(f"🤖 Agent Query: {user_input}")
        # Convert history for the agent
        history = convert_messages(messages)
        result = await app_state["executor"].ainvoke({
            "input": user_input,
            "chat_history": history
        })
        content = result["output"]
        content = result["output"]

        if not content or content.strip() == "":
            content = "I encountered an issue processing that list. Please try again or a different question."

    return {
        "id": f"chatcmpl-{int(time.time())}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "qwen2.5-mcp-agent",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}]
    }

@app.get("/v1/models")
async def list_models():
    return {"object": "list", "data": [{"id": "qwen2.5-mcp-agent", "object": "model", "owned_by": "local"}]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
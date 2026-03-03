import asyncio
from langchain_ollama import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_classic.agents import AgentExecutor
from langchain_classic.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

## General Agent code structure. main.py is geared towards Openweb UI, which needs OpenAI chat compatibility.

async def main():
    # 1. Setup Model (Qwen 2.5 14b)
    model = ChatOllama(model="qwen2.5:14b", temperature=0)

    # 2. Connect to MCP & Get Tools
    client = MultiServerMCPClient({
        "rest_countries": {
            "command": "docker",
            "args": ["run", "-i", "--rm", "restcountries-mcp"],
            "transport": "stdio",
        }
    })

    # 3. Simplify Agent Creation
    tools = await client.get_tools()
    
    # We define the prompt once. This is cleaner than injecting it into a loop.
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use tools for country data."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # Construct the tool-calling agent
    agent = create_tool_calling_agent(model, tools, prompt)
    
    # Create the executor (the runtime for the agent)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # 4. Run it
    query = "What is the capital and population of Peru?"
    result = await agent_executor.ainvoke({"input": query})
    
    print(f"\nFinal Answer: {result['output']}")

if __name__ == "__main__":
    asyncio.run(main())
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    print("🚀 Spawning MCP server via stdio...")

    client = MultiServerMCPClient(
        {
            "rest_countries": {
                "command": "python",
                "args": ["mcp_server.py", "--stdio"],
                "transport": "stdio",
            }
        }
    )

    # print("🔌 Connecting to local MCP server via SSE...")
    # # Connect to local running MCP (or Docker)
    # client = MultiServerMCPClient(
    #     {
    #         "rest_countries": {
    #             "url": "http://127.0.0.1:8000", # Rancher desktop has some issue with localhost
    #             "transport": "sse",
    #         }
    #     }
    # )

    tools = await client.get_tools()

    print(f"✅ Tools discovered: {[t.name for t in tools]}")

    # Find tool by name
    search_tool = next(t for t in tools if t.name == "search_country_by_name")

    print("\n📡 Calling tool...\n")

    result = await search_tool.ainvoke({"name": "Japan"})

    print("📦 Result:")
    print(result)

    print("\n🛑 Done.")


if __name__ == "__main__":
    asyncio.run(main())
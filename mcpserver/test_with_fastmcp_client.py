import asyncio
from fastmcp.client import Client
from fastmcp.client.transports.stdio import StdioTransport


async def main():
    print("🚀 Starting persistent MCP subprocess...")

    transport = StdioTransport(
        command="python",
        args=["mcp_server.py", "--stdio"],
    )

    # Client is an async context manager
    async with Client(transport=transport) as client:

        print("✅ Connected. Subprocess is alive.\n")

        tools = await client.list_tools()
        print("🔧 Available tools:")
        for t in tools:
            print("  -", t.name)

        print("\n📡 Calling tool search_country_by_name for Japan")
        result = await client.call_tool(
            "search_country_by_name",
            {"name": "Japan"},
        )
        print("Result:", result)

    print("\n🛑 Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
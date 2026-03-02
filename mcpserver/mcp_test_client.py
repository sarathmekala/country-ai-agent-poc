import asyncio
from fastmcp import Client


async def main():
    async with Client("mcp_server.py") as client:

        # List available tools
        tools = await client.list_tools()
        print("Available tools:", tools)

        # Call get_country_by_name
        result = await client.call_tool(
            "get_country_by_name",
            {"name": "peru"}
        )
        print("\nCountry by name:\n", result)

        # Call get_countries_by_fields
        result = await client.call_tool(
            "get_countries_by_fields",
            {"fields": ["name", "capital", "population"]}
        )
        print("\nCountries by fields:\n", result)


if __name__ == "__main__":
    asyncio.run(main())
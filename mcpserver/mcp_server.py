import httpx
from fastmcp import FastMCP

BASE_URL = "https://restcountries.com/v3.1"

mcp = FastMCP("restcountries-mcp")

# ---------------------------------------------------
# MCP Tools
# ---------------------------------------------------

@mcp.tool()
async def get_country_by_name(name: str):
    """
    Get detailed country information by country name.
    Example: Peru, India, France
    """
    url = f"{BASE_URL}/name/{name}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise Exception(
            f"Error fetching country '{name}': "
            f"{response.status_code} - {response.text}"
        )

    return response.json()


@mcp.tool()
async def get_countries_by_fields(fields: list[str]):
    """
    Get all countries but only return specified fields.
    Example: ["name", "capital", "population"]
    """
    fields_param = ",".join(fields)
    url = f"{BASE_URL}/all?fields={fields_param}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise Exception(
            f"Error fetching fields {fields}: "
            f"{response.status_code} - {response.text}"
        )

    return response.json()


# ---------------------------------------------------
# Run Server
# ---------------------------------------------------

if __name__ == "__main__":
    mcp.run()
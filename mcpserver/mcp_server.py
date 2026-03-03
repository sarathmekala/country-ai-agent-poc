import httpx
from fastmcp import FastMCP

BASE_URL = "https://restcountries.com/v3.1"

mcp = FastMCP("restcountries-mcp")

# ---------------------------------------------------
# MCP Tools
# ---------------------------------------------------

@mcp.tool()
async def search_country_by_name(name: str) -> str:
    """Fetches key data (capital, pop, area) for a country."""
    url = f"https://restcountries.com/v3.1/name/{name}?fullText=true"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return f"Error: Country '{name}' not found."
            
        data = response.json()
        
        # KEY PERFORMANCE TUNING: Filtering the blob
        optimized_list = []
        for country in data:
            optimized_list.append({
                "common_name": country.get("name", {}).get("common"),
                "capital": country.get("capital", ["N/A"])[0],
                "population": f"{country.get('population', 0):,}",
                "area_km2": country.get("area"),
                "region": country.get("region")
            })
            
        return str(optimized_list) # can be something like response.json() as well.


# ---------------------------------------------------
# Run Server
# ---------------------------------------------------

if __name__ == "__main__":
    import sys

    if "--stdio" in sys.argv:
        mcp.run(transport="stdio")
    else:
        mcp.run(transport="sse", host="0.0.0.0", port=8000)
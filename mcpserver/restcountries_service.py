import httpx
from typing import List, Dict, Any


BASE_URL = "https://restcountries.com/v3.1"


class RestCountriesService:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_country_by_name(self, name: str) -> List[Dict[str, Any]]:
        url = f"{BASE_URL}/name/{name}"
        response = await self.client.get(url)

        if response.status_code != 200:
            raise Exception(
                f"Error fetching country '{name}': {response.status_code} - {response.text}"
            )

        return response.json()

    async def get_countries_by_fields(self, fields: List[str]) -> List[Dict[str, Any]]:
        fields_param = ",".join(fields)
        url = f"{BASE_URL}/all?fields={fields_param}"
        response = await self.client.get(url)

        if response.status_code != 200:
            raise Exception(
                f"Error fetching fields {fields}: {response.status_code} - {response.text}"
            )

        return response.json()

    async def close(self):
        await self.client.aclose()
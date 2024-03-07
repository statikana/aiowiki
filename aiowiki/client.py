from types import TracebackType
from typing import Type
from aiohttp import ClientSession

from aiowiki.constants import BASE_URL
from aiowiki.models.enums import Language
from aiowiki.models.results import SearchPageResult


class WikiClient:
    def __init__(
        self,
        *,
        access_token: str,
        app: str,
        language: Language = Language.EN
    ):
        self.session = ClientSession(
            base_url=BASE_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0."
            },
            raise_for_status=True
        )
        self.path: str = f"/core/v1/wikipedia/{language.value}"
    
    async def search_page(self, query: str, /, *, limit: int = 10):
        response = await self.session.get(
            f"{self.path}/search/page",
            params={
                "q": query,
                "limit": limit
            }
        )
        return SearchPageResult.from_json(await response.json())

    async def __aenter__(self):
        return self

    async def __aexit__(self, *results):
        return self

    
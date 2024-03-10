import datetime

from httpx import AsyncClient

from aiowiki.constants import BASE_URL
from aiowiki.models.enums import EventType, Language, Project
from aiowiki.models.results import (
    ArticleURLs,
    FeaturedContent,
    OnThisDay,
    SearchPageResult,
)


class WikiClient:
    """The main client through which to access the wrapper's functionality."""

    def __init__(
        self,
        *,
        project: Project = Project.WIKIPEDIA,
        language: Language = Language.ENGLISH,
        proxy: str | None = None,
    ) -> None:
        """Creates a new WikiClient instance.

        Args:
            project (Project): The selected Wikimedia project for the client. You probably want Wikipedia (articles) or Commons (images, videos).
            language (Language): The selected language for the client. This is not used in multilingual projects, such as the Commons.
            proxy (str): Optional. The proxy to use for making requests. Defaults to None.
        """
        self._session = AsyncClient(proxy=proxy, timeout=10)

        self.project = project
        """The selected Wikimedia project for the client. You probably want Wikipedia (articles) or Commons (images, videos)."""

        self.language = language
        """The selected language for the client. This is not used in multilingual projects, such as the Commons."""

        self.core = _CoreREST(self, "/core/v1")
        """Module for interacting with Wikimedia's 'Core' REST API."""

        self.feed = Feed(self, "/feed/v1")
        """Module for interacting with Wikimedia's 'Feed' API."""


class _WikiModule:
    def __init__(self, client: WikiClient, base: str) -> None:
        self._client = client
        self._base_url = f"{BASE_URL}{base}"


class _CoreREST(_WikiModule):
    async def search_content(self, query: str, /, *, limit: int = 10) -> list[SearchPageResult]:
        """
        Searches for pages matching the query and returns a list of `SearchPageResult` objects.

        Args:
            query (str): The search query.
            limit (int): The maximum number of results to return, between 1 and 100. Defaults to 10.

        URL:
            GET /{project}/{language}/search/page

        Returns:
            list[SearchPageResult]: A list of search results.
        """
        response = await self._client._session.get(
            f"{self._base_url}/{self._client.project.value}/{self._client.language.value}/search/page",
            params={"q": query, "limit": limit},
        )
        response.raise_for_status()
        return [
            SearchPageResult.from_json(result) for result in response.json()["pages"]
        ]

    async def search_titles(self, query: str, /, *, limit: int = 10) -> list[SearchPageResult]:
        """
        Searches for page titles matching the query and returns a list of `SearchPageResult` objects.

        URL:
            GET /{project}/{language}/search/title

        Args:
            query (str): The search query.
            limit (int): The maximum number of results to return, between 1 and 100. Defaults to 10.

        Returns:
            list[SearchPageResult]: A list of search results.
        """
        response = await self._client._session.get(
            f"{self._base_url}/{self._client.project.value}/{self._client.language.value}/search/title",
            params={"q": query, "limit": limit},
        )
        response.raise_for_status()
        return [
            SearchPageResult.from_json(result) for result in response.json()["pages"]
        ]


class Feed(_WikiModule):
    async def featured_content(self, date: datetime.date = datetime.date.today()) -> FeaturedContent:
        """
        Fetches the featured content for a given date.

        Specifically: daily featured article, picture of the day, most read article yesterday, and most

        Args:
            date (datetime.date): The date to fetch featured content for. Defaults to today.

        URL:
            GET /wikipedia/{language}/featured/{YYYY}/{MM}/{DD}
        """
        fmt_date = date.strftime("%Y/%m/%d")
        response = await self._client._session.get(
            f"{self._base_url}/wikipedia/{self._client.language.value}/featured/{fmt_date}",
        )
        response.raise_for_status()
        return FeaturedContent.from_json(response.json())

    async def onthisday(
        self,
        date: datetime.date = datetime.date.today(),
        type: EventType = EventType.ALL,
    ) -> OnThisDay:
        """
        Fetches the 'on this day' events for a given day and month.

        Args:
            date (datetime.date): The date to fetch events for. The 'year' component of the date is ignored. Defaults to today.
            type (EventType): The type of events to fetch. Defaults to EventType.all.

        URL:
            GET /wikipedia/{language}/onthisday/{type}/{MM}/{DD}
        """
        fmt_date = f"{str(date.month).rjust(2, '0')}/{str(date.day - 1).rjust(2, '0')}"
        response = await self._client._session.get(
            f"{self._base_url}/wikipedia/{self._client.language.value}/onthisday/{type.value}/{fmt_date}",
            params={"type": type.value},
        )
        response.raise_for_status()
        return OnThisDay.from_json(response.json())

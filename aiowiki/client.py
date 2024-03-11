import datetime

from httpx import AsyncClient

from aiowiki.constants import BASE_URL
from aiowiki.models.enums import EventType, Language, Project
from aiowiki.models.results import (
    FeaturedContent,
    File,
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
        self._session = AsyncClient(proxy=proxy)

        self._project = project

        self._language = language

        self.core = _Core(self, "/core/v1")
        """Module for interacting with Wikimedia's 'Core' REST API."""

        self.feed = _Feed(self, "/feed/v1")
        """Module for interacting with Wikimedia's 'Feed' API."""
    
    @property
    def project(self) -> Project:
        """Get the selected Wikimedia project for the client."""
        return self._project

    @project.setter
    def project(self, project: Project) -> None:
        """Set the selected Wikimedia project for the client."""
        self._project = project

    @property
    def language(self) -> Language:
        """Get the selected language for the client."""
        return self._language

    @language.setter
    def language(self, language: Language) -> None:
        """Set the selected language for the client."""
        self._language = language


class _WikiModule:
    def __init__(self, client: WikiClient, base: str) -> None:
        self._client = client
        self._base_url = f"{BASE_URL}{base}"


class _Core(_WikiModule):
    async def search_content(self, query: str, /, *, limit: int = 10) -> list[SearchPageResult]:
        """
        Searches wiki pages for the given search terms, and returns matching pages. 

        Args:
            query (str): The search query.
            limit (int): The maximum number of results to return, between 1 and 100. Defaults to 10.

        Path:
            GET /{project}/{language}/search/page

        Returns:
            list[SearchPageResult]: A list of search results.
        """
        response = await self._client._session.get(
            f"{self._base_url}/{self._client._project.value}/{self._client._language.value}/search/page",
            params={"q": query, "limit": limit},
        )
        response.raise_for_status()
        return [
            SearchPageResult._from_json(result) for result in response.json()["pages"]
        ]

    async def search_titles(self, query: str, /, *, limit: int = 10) -> list[SearchPageResult]:
        """
        Searches wiki page titles, and returns pages witmm.h titles that begin with the provided search terms. 
        You can use this endpoint as an autocomplete search that automatically suggests relevant pages by title. 

        Args:
            query (str): The search query.
            limit (int): The maximum number of results to return, between 1 and 100. Defaults to 10.

        Path:
            GET /{project}/{language}/search/title

        Returns:
            list[SearchPageResult]: A list of search results.
        """
        response = await self._client._session.get(
            f"{self._base_url}/{self._client._project.value}/{self._client._language.value}/search/title",
            params={"q": query, "limit": limit},
        )
        response.raise_for_status()
        return [
            SearchPageResult._from_json(result) for result in response.json()["pages"]
        ]
    
    async def get_description(self, title: str) -> str:
        """
        Returns a description of a page. A page description is a short, plain-text phrase summarizing the page's topic. 
        While descriptions are available for most pages, some pages may not have a description.

        Args:
            title (str): Wiki page title with spaces replaced with underscores. This IS case-sensitive.
        
        Path:
            GET /core/v1/{project}/{language}/page/{title}/description 
        """
        
        response = await self._client._session.get(
            f"{self._base_url}/{self._client._project.value}/{self._client._language.value}/page/{title}/description",
        )
        response.raise_for_status()
        return response.json()["description"]
    
    async def get_file(self, filename: str) -> File:
        response = await self._client._session.get(
            f"{self._base_url}/commons/file/File:{filename}",
        )
        response.raise_for_status()
        return File._from_json(response.json())


class _Feed(_WikiModule):
    async def featured_content(self, date: datetime.date = datetime.date.today()) -> FeaturedContent:
        """
        Fetches the featured content for a given date.

        Specifically: daily featured article, picture of the day, most read article yesterday, and most

        Args:
            date (datetime.date): The date to fetch featured content for. Defaults to today.

        Path:
            GET /wikipedia/{language}/featured/{YYYY}/{MM}/{DD}
        """
        fmt_date = date.strftime("%Y/%m/%d")
        response = await self._client._session.get(
            f"{self._base_url}/wikipedia/{self._client._language.value}/featured/{fmt_date}",
        )
        response.raise_for_status()
        return FeaturedContent._from_json(response.json())

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

        Path:
            GET /wikipedia/{language}/onthisday/{type}/{MM}/{DD}
        """
        fmt_date = f"{str(date.month).rjust(2, '0')}/{str(date.day - 1).rjust(2, '0')}"
        response = await self._client._session.get(
            f"{self._base_url}/wikipedia/{self._client._language.value}/onthisday/{type.value}/{fmt_date}",
            params={"type": type.value},
        )
        response.raise_for_status()
        return OnThisDay._from_json(response.json())
    
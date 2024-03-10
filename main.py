import asyncio

import aiowiki
from env import PROXY
from logging_setup import setup


async def main() -> None:
    wiki = aiowiki.WikiClient(proxy=PROXY)
    articles = await wiki.core.search_content("Python", limit=1)
    print([a.title for a in articles])


if __name__ == "__main__":
    setup()
    asyncio.run(main())

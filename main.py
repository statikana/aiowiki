import asyncio
import aiowiki
from env import PROXY

from logging_setup import setup


async def main():
    wiki = aiowiki.WikiClient(proxy=PROXY)
    articles = await wiki._project("Python", limit=1)
    print([a.title for a in articles])


if __name__ == "__main__":
    setup()
    asyncio.run(main())

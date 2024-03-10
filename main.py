import asyncio
import aiowiki
from env import PROXY

from logging_setup import setup


async def main():
    wiki = aiowiki.WikiClient(proxy=PROXY)
    otd = await wiki.feed.onthisday()
    print(otd.births)
if __name__ == "__main__":
    setup()
    asyncio.run(main())

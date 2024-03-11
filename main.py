import asyncio

import aiowiki
from env import PROXY
from logging_setup import setup


async def main() -> None:
    wiki = aiowiki.WikiClient(proxy=PROXY)
    file = await wiki.core.get_file("The_Blue_Marble.jpg")
    print(file.original.url)

if __name__ == "__main__":
    setup()
    asyncio.run(main())

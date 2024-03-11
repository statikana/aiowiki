import asyncio

import awiki
from env import PROXY
from logging_setup import setup


async def main() -> None:
    wiki = awiki.WikiClient(proxy=PROXY)
    file = await wiki.core.get_file("Person.jpg")
    print(file.original.url)

if __name__ == "__main__":
    setup()
    asyncio.run(main())

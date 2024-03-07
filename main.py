import asyncio
from aiowiki.client import WikiClient
from env import *

data = {
    "access_token": WIKIMEDIA_ACCESS_TOKEN,
    "app": "AIOWiki Test (contact@statikana.dev)"
}

async def main():
    wiki = WikiClient(**data)
    print(wiki.session.headers)
    print(await wiki.search_page("Earth", limit=3))


if __name__ == "__main__":
    asyncio.run(main())
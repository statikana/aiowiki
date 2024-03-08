import asyncio
import aiowiki
from env import PROXY


async def main():
    wiki = aiowiki.WikiClient(project=aiowiki.Project.WIKIPEDIA, proxy=PROXY)
    results = await wiki.core.search_content("Python", limit=5)
    for r in results:
        print(r.title)


if __name__ == "__main__":
    asyncio.run(main())
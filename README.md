# awiki

a basic asynchronous wrapper for the wikimedia API.

awiki currently only supports anonymous actions (ie., getting and searching for pages),
and does not support editing or creating new pages.


## installation

your favorite flavor of the following:
```bash
python3 -m pip install -U awiki
```

## quick overview

the main class is `awiki.WikiClient`. Each section of the wikimedia API is separated within this class.

* WikiClient.core: Searching for pages and getting file data

* WikiClient.feed: Getting featured content such as things in the news and 

## examples

searching for articles called "Python":

```python
import asyncio

import awiki

async def main():
    # create a new instance of the wiki client
    wiki = awiki.WikiClient()

    # Searches wiki pages for the given search terms, and returns matching pages.
    pages = await wiki.search_content("Python", limit=25)

    for p in pages:
        print(f"{p.title}: {p.description} (https://en.wikipedia.org/wiki/{p.key})")


if __name__ == "__main__":
    asyncio.run(main())
```

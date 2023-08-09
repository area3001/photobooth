import asyncio
import aiohttp
from io import BytesIO


def get_file_content(filename):
    with open(filename, "rb") as fh:
        buf = BytesIO(fh.read())
    return buf


async def upload(filename):
    url = "https://discord.com/api/webhooks/CHANNEL/TOKEN"

    file_content = await asyncio.to_thread(get_file_content, filename)
    formdata = aiohttp.FormData()
    formdata.add_field('file', file_content, filename=filename)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=formdata) as response:
            print(response.status)
            print(await response.text())

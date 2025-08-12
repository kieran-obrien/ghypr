async def download_file(client, url, save_path):
    """Download a file asynchronously using httpx."""
    async with client.stream("GET", url, follow_redirects=True) as response:
        response.raise_for_status()
        with open(save_path, "wb") as f:
            async for chunk in response.aiter_bytes():
                f.write(chunk)   
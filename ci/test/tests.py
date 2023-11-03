import httpx


async def healthcheck_test(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        assert response.status_code == 200
        assert response.text == "OK"

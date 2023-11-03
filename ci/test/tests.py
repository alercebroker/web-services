import httpx


async def healthcheck_test(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        assert response.status_code == 200
        assert response.text == "OK"

tests_dict = {
    "healthcheck": healthcheck_test,
}

if __name__ == "__main__":
    import sys
    test = sys.argv[1]
    args = sys.argv[2].split(",")
    tests_dict[test](*args)

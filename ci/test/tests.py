import httpx


def healthcheck_test(url: str):
    with httpx.Client() as client:
        response = client.get(url)
        assert response.status_code == 200
        assert response.json() == "OK"


tests_dict = {
    "healthcheck": healthcheck_test,
}

if __name__ == "__main__":
    import sys

    test = sys.argv[1]
    args = sys.argv[2].split(",")
    tests_dict[test](*args)

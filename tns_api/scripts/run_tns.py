import os

import uvicorn


def run():
    port = os.getenv("PORT", default=8000)
    root_path = os.getenv("ROOT_PATH", default="/")
    uvicorn.run("tns_api.api:app", host="0.0.0.0", port=int(port), root_path=root_path)


if __name__ == "__main__":
    run()

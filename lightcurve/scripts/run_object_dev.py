import os

import uvicorn


def run():
    port = os.getenv("PORT", default=8000)
    uvicorn.run("object_api.api:app", port=int(port), reload=True, reload_dirs=[".", "../libs"])

if __name__ == "__main__":
    run()

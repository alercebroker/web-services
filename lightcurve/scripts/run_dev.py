import os

import uvicorn


def run():
    port = os.getenv("PORT", default=8000)
    uvicorn.run("api.api:app", port=port, reload=True)

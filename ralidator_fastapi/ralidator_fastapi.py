from ralidator_core.ralidator_core import (
    Ralidator,
    RalidatorCoreSettingsFactory,
)
from ralidator_core.settings_factory import json
from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, StreamingResponse, JSONResponse
from starlette.types import ASGIApp
from starlette.concurrency import iterate_in_threadpool
import re


class RalidatorStarlette(BaseHTTPMiddleware):
    def __init__(
        self, app: ASGIApp, config: dict, filters_map: dict, ignore_paths: list
    ) -> None:
        super().__init__(app)
        self.ralidator_settings = RalidatorCoreSettingsFactory.from_dict(
            config
        )
        self.filters_map = filters_map
        self.ignore_paths = ignore_paths

    async def response_to_json(self, response: StreamingResponse | Response):
        if isinstance(response, StreamingResponse):
            response_body = [
                section async for section in response.body_iterator
            ]
            response.body_iterator = iterate_in_threadpool(iter(response_body))
            return json.loads(response_body[0])
        return json.loads(response.body)

    def generate_data(self, data: list):
        for d in data:
            yield d

    async def apply_ralidator_filters(
        self, response: StreamingResponse | Response, ralidator: Ralidator
    ) -> Response:
        data = await self.response_to_json(response)
        data = ralidator.apply_filters(data)
        if isinstance(data, list):
            response = StreamingResponse(self.generate_data(data))
            return response
        else:
            return JSONResponse(data)

    def apply_ralidator_auth(self, request: Request, ralidator: Ralidator):
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header:
            if re.search("bearer", auth_header, re.IGNORECASE) is None:
                raise ValueError("Malformed Authorization header")
            try:
                token = auth_header.split()[1]
            except Exception:
                raise ValueError("Malformed Authorization header")
        ralidator.authenticate_token(token)

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in self.ignore_paths:
            return await call_next(request)
        ralidator = Ralidator(self.ralidator_settings, self.filters_map)
        request.state.ralidator = ralidator
        self.apply_ralidator_auth(request, ralidator)
        response = await call_next(request)
        response = await self.apply_ralidator_filters(response, ralidator)
        return response

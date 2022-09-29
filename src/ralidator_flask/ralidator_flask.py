from flask import _request_ctx_stack, request, abort
from ralidator_core.ralidator_core import Ralidator
from ralidator_core.settings_factory import RalidatorCoreSettingsFactory
import re
import json


class RalidatorFlask(object):
    def __init__(self, app=None):
        self.app = app
        self.filters_map = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.ralidator_settings = RalidatorCoreSettingsFactory.from_dict(
            app.config["RALIDATOR_SETTINGS"]
        )
        self.filters_map = app.config["FILTERS_MAP"]

        @app.before_request
        def before_request():
            ctx = self.set_ralidator_on_context()
            auth_header = request.headers.get("Authorization")
            token = None
            if auth_header:
                if re.search("bearer", auth_header, re.IGNORECASE) is None:
                    abort(403, "Malformed Authorization header")
                try:
                    token = auth_header.split()[1]
                except Exception:
                    abort(403, "Malformed Authorization header")
            ctx.ralidator.authenticate_token(token)

        @app.after_request
        def after_request(response):
            if response.status_code < 400:
                if response.is_json:
                    filtered_data = self.ralidator.apply_filters(
                        response.get_json()
                    )
                    response.set_data(json.dumps(filtered_data))
            return response

    def set_ralidator_on_context(self):
        ctx = _request_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, "ralidator"):
                ctx.ralidator = Ralidator(
                    self.ralidator_settings, self.filters_map
                )
        return ctx

    @property
    def ralidator(self) -> Ralidator:
        ctx = self.set_ralidator_on_context()
        return ctx.ralidator

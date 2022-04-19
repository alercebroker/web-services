from flask import _request_ctx_stack
from ralidator_core.ralidator_core import Ralidator
from ralidator_core.settings_factory import RalidatorCoreSettingsFactory


class RalidatorFlask(object):
    def __init__(self, app=None):
        self.app = app
        self.filters_map = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.ralidator_settings = RalidatorCoreSettingsFactory()
        self.filters_map = app.config["FILTERS_MAP"]

        @app.before_request
        def before_request():
            self.set_ralidator_on_context()

        @app.after_request
        def after_request(response):
            if response.status_code < 400:
                response.set_data(
                    self.ralidator.apply_filters(response.get_json())
                )
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

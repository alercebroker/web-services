import copy
from typing import Any

from lightcurve_api.routes.htmx.parsers import ConfigState

from ...models.lightcurve import Lightcurve


class Result:
    echart_options: dict[str, Any]
    lightcurve: Lightcurve
    config_state: ConfigState

    def __init__(self, echart_options: dict[str, Any], lightcurve: Lightcurve, config_state: ConfigState, period):
        self.echart_options = echart_options
        self.lightcurve = lightcurve
        self.config_state = config_state
        self.period = period

    def copy(self):
        return Result(
            echart_options=copy.deepcopy(self.echart_options),
            lightcurve=Lightcurve(
                detections=copy.deepcopy(self.lightcurve.detections),
                non_detections=copy.deepcopy(self.lightcurve.non_detections),
                forced_photometry=copy.deepcopy(self.lightcurve.forced_photometry),
            ),
            config_state=self.config_state.model_copy(deep=True),
            period=copy.deepcopy(self.period),
        )

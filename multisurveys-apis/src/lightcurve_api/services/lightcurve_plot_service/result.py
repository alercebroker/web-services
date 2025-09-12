import copy
from typing import Any

from ...models.lightcurve import Lightcurve


class Result:
    echart_options: dict[str, Any]
    lightcurve: Lightcurve

    def __init__(self, echart_options: dict[str, Any], lightcurve: Lightcurve):
        self.echart_options = echart_options
        self.lightcurve = lightcurve

    def copy(self):
        return Result(
            echart_options=copy.deepcopy(self.echart_options),
            lightcurve=Lightcurve(
                detections=copy.deepcopy(self.lightcurve.detections),
                non_detections=copy.deepcopy(self.lightcurve.non_detections),
                forced_photometry=copy.deepcopy(self.lightcurve.forced_photometry),
            ),
        )

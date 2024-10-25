import { jdToDate } from "./astro-dates.js";
import { LightCurveOptions } from "./lc-utils.js";

export class DifferenceLightCurveOptions extends LightCurveOptions {
  constructor(
    detections,
    nonDetections,
    forcedPhotometry,
    fontColor,
    flux = false,
  ) {
    super(
      fontColor,
      "Difference Magnitude",
    );
    this.detections = detections;
    this.nonDetections = nonDetections;
    this.forcedPhotometry = forcedPhotometry;
    this.getSeries(flux);
    this.getLegend();
    this.getBoundaries();
  }

  getSeries(flux) {
    const bands = new Set(this.detections.map((item) => item.fid));
    const ndBands = new Set(this.nonDetections.map((item) => item.fid));
    const fpBands = new Set(this.forcedPhotometry.map((item) => item.fid));
    let detections = this.detections;
    let forcedPhotometry = this.forcedPhotometry;
    if (flux) {
      detections = LightCurveOptions.magToFlux(this.detections);
      forcedPhotometry = LightCurveOptions.magToFlux(this.forcedPhotometry);
      this.options.yAxis.inverse = false;
      this.options.yAxis.name = "Flux [uJy]";
      this.options.yAxis.nameLocation = "end";
      this.options.title.text = "Difference Flux";
    }
    this.addDetections(detections, bands, flux);
    this.addErrorBars(detections, bands, flux);
    this.addForcedPhotometry(forcedPhotometry, fpBands, flux);
    this.addErrorBarsForcedPhotometry(forcedPhotometry, fpBands, flux);
    if (!flux) {
      this.addNonDetections(this.nonDetections, ndBands);
    }
  }

  addDetections(detections, bands, flux) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name,
        type: "scatter",
        scale: true,
        color: this.bandMap[band].color,
        symbolSize: 6,
        encode: {
          x: 0,
          y: 1,
        },
      };
      serie.data = this.formatDetections(detections, band, flux);
      this.options.series.push(serie);
    });
  }

  addErrorBars(detections, bands, flux) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name,
        type: "custom",
        scale: true,
        color: this.bandMap[band].color,
        renderItem: this.renderError,
      };
      serie.data = this.formatError(detections, band, flux);
      this.options.series.push(serie);
    });
  }

  addErrorBarsForcedPhotometry(forcedPhotometry, bands, flux) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name + " forced photometry",
        type: "custom",
        scale: true,
        color: this.bandMap[band].color,
        renderItem: this.renderError,
      };
      serie.data = this.formatError(forcedPhotometry, band, flux, true);
      this.options.series.push(serie);
    });
  }

  addNonDetections(nonDetections, bands) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name + " non-detections",
        type: "scatter",
        scale: true,
        color: this.hexToRGB(this.bandMap[band].color, 0.5),
        symbolSize: 6,
        symbol:
          "path://M0,49.017c0-13.824,11.207-25.03,25.03-25.03h438.017c13.824,0,25.029,11.207,25.029,25.03L262.81,455.745c0,0-18.772,18.773-37.545,0C206.494,436.973,0,49.017,0,49.017z",
      };
      serie.data = this.formatNonDetections(nonDetections, band);
      this.options.series.push(serie);
    });
  }

  addForcedPhotometry(forcedPhotometry, bands, flux) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name + " forced photometry",
        type: "scatter",
        scale: true,
        color: this.bandMap[band].color,
        symbolSize: 6,
        symbol: "path://M0,0 L0,10 L10,10 L10,0 Z",
        encode: {
          x: 0,
          y: 1,
        },
      };
      serie.data = this.formatForcedPhotometry(forcedPhotometry, band, flux);
      this.options.series.push(serie);
    });
  }

  formatError(detections, band, flux, forced = false) {
    const magLimit = flux ? 999999 : 99;
    const eMagLimit = flux ? 999999 : 1;
    return detections
      .filter(function (x) {
        if (forced && "extra_fields" in x) {
          if ("distnr" in x["extra_fields"]) {
            return (
              x["extra_fields"]["distnr"] >= 0 &&
              x.fid === band &&
              x.e_mag <= eMagLimit &&
              x.mag <= magLimit
            );
          }
        }
        return x.fid === band && x.e_mag <= eMagLimit && x.mag <= magLimit;
      })
      .map(function (x) {
        return [x.mjd, x.mag - x.e_mag, x.mag + x.e_mag];
      });
  }

  formatDetections(detections, band, flux) {
    const magLimit = flux ? 999999 : 99;
    const eMagLimit = flux ? 999999 : 1;
    return detections
      .filter(function (x) {
        return x.fid === band && x.mag <= magLimit && x.e_mag <= eMagLimit;
      })
      .map(function (x) {
        return [x.mjd, x.mag, x.candid, x.e_mag, x.isdiffpos];
      });
  }

  formatForcedPhotometry(forcedPhotometry, band, flux) {
    const magLimit = flux ? 999999 : 99;
    const eMagLimit = flux ? 999999 : 1;
    return forcedPhotometry
      .filter(function (x) {
        if ("distnr" in x["extra_fields"]) {
          return (
            x["extra_fields"]["distnr"] >= 0 &&
            x.fid === band &&
            x.mag <= magLimit &&
            x.e_mag <= eMagLimit
          );
        }
        return x.fid === band && x.mag <= magLimit && x.e_mag <= eMagLimit;
      })
      .map(function (x) {
        return [x.mjd, x.mag, "no-candid", x.e_mag, x.isdiffpos];
      });
  }

  formatNonDetections(nonDetections, band) {
    return nonDetections
      .filter(function (x) {
        return x.fid === band && x.diffmaglim > 10 && x.diffmaglim <= 25;
      })
      .map(function (x) {
        return [x.mjd, x.diffmaglim];
      });
  }

  getLegend() {
    let legend = this.options.series
      .filter((x) => x.data.length > 0)
      .map((x) => x.name);
    this.options.legend.data = legend;
  }

  getBoundaries() {
    const sigmas = this.options.series
      .filter((x) => x.type === "scatter")
      .map((x) => x.data)
      .flat()
      .map((x) => x[3])
      .filter((x) => x < 99);
    const maxSigma = sigmas.reduce((a, b) => Math.max(a, b), -Infinity);
    this.options.yAxis.min = (x) => (x.min - (maxSigma + 0.1)).toFixed(1);
    this.options.yAxis.max = (x) => (x.max + maxSigma + 0.1).toFixed(1);
  }

  lcDifferenceOnClick(detection) {
    const date = jdToDate(detection.value[0]).toUTCString().slice(0, -3) + "UT";
    return {
      mjd: detection.value[0],
      date,
      index: this.detections.findIndex((x) => x.mjd === detection.value[0]),
    };
  }
}

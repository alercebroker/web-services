import { LightCurveOptions } from "./lc-utils.js";

export class FoldedLightCurveOptions extends LightCurveOptions {
  constructor(detections, forcedPhotometry, fontColor, period, flux) {
    super(detections, [], forcedPhotometry, fontColor, "Folded Light Curve");
    this.detections = detections;
    this.forcedPhotometry = forcedPhotometry;
    this.period = period;
    this.getSeries(flux);
    this.getLegend();
    this.getBoundaries();
  }

  getSeries(flux) {
    const bands = Array.from(new Set(this.detections.map((item) => item.fid)));
    const fpBands = Array.from(
      new Set(this.forcedPhotometry.map((item) => item.fid)),
    );
    let detections = this.detections;
    let forcedPhotometry = this.forcedPhotometry;
    if (flux) {
      detections = LightCurveOptions.magToFlux(this.detections, true);
      forcedPhotometry = LightCurveOptions.magToFlux(
        this.forcedPhotometry,
        true,
      );
      this.options.yAxis.inverse = false;
      this.options.yAxis.name = "Flux [uJy]";
      this.options.yAxis.nameLocation = "end";
      this.options.title.text = "Total Flux";
    }
    this.addDetections(detections, bands, this.period, flux);
    this.addErrorBars(detections, bands, this.period, flux);
    this.addForcedPhotometry(forcedPhotometry, fpBands, this.period, flux);
    this.addErrorBarsForcedPhotometry(
      forcedPhotometry,
      fpBands,
      this.period,
      flux,
    );
  }

  addDetections(detections, bands, period, flux) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name,
        type: "scatter",
        scale: true,
        color: this.bandMap[band].color,
        symbolSize: band < 100 ? 6 : 3,
        symbol: band < 100 ? "circle" : "square",
        encode: {
          x: 0,
          y: 1,
        },
        zlevel: band < 100 ? 10 : 0,
      };
      serie.data = this.formatDetections(detections, band, period, flux);
      this.options.series.push(serie);
    });
  }

  addForcedPhotometry(detections, bands, period, flux) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name + " forced photometry",
        type: "scatter",
        scale: true,
        color: this.bandMap[band].color,
        symbolSize: 6,
        symbol: "square",
        encode: {
          x: 0,
          y: 1,
        },
        zlevel: 10,
      };
      serie.data = this.formatForcedPhotometry(detections, band, period, flux);
      this.options.series.push(serie);
    });
  }

  addErrorBars(detections, bands, period, flux) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name,
        type: "custom",
        scale: true,
        color: this.bandMap[band].color,
        renderItem: this.renderError,
      };
      serie.data = this.formatError(detections, band, period, flux);
      this.options.series.push(serie);
    });
  }

  addErrorBarsForcedPhotometry(detections, bands, period, flux) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name + " forced photometry",
        type: "custom",
        scale: true,
        color: this.bandMap[band].color,
        renderItem: this.renderError,
      };
      serie.data = this.formatError(detections, band, period, flux);
      this.options.series.push(serie);
    });
  }

  formatDetections(detections, band, period, flux) {
    const maglim = flux ? 999999 : 99;
    const emaglim = flux ? 999999 : 1;
    const folded1 = detections
      .filter((x) => {
        return (
          x.fid === band &&
          x.corrected &&
          x.mag_corr > 0 &&
          x.mag_corr <= maglim &&
          x.e_mag_corr_ext < emaglim
        );
      })
      .map((x) => {
        const phase = (x.mjd % period) / period;
        return [
          phase,
          x.mag_corr,
          x.candid !== undefined ? x.candid : x.objectid,
          x.e_mag_corr_ext,
          x.isdiffpos !== undefined ? x.isdiffpos : x.field,
        ];
      });
    const folded2 = folded1.map((x) => {
      return [x[0] + 1, x[1], x[2], x[3], x[4]];
    });
    return folded1.concat(folded2);
  }

  formatForcedPhotometry(detections, band, period, flux) {
    const maglim = flux ? 999999 : 99;
    const emaglim = flux ? 999999 : 1;
    const folded1 = detections
      .filter((x) => {
        if ("extra_fields" in x) {
          if ("distnr" in x["extra_fields"]) {
            return (
              x["extra_fields"]["distnr"] >= 0 &&
              x.fid === band &&
              x.corrected &&
              x.mag_corr > 0 &&
              x.mag_corr <= maglim &&
              x.e_mag_corr_ext < emaglim
            );
          }
        }
        return (
          x.fid === band &&
          x.corrected &&
          x.mag_corr > 0 &&
          x.mag_corr <= maglim &&
          x.e_mag_corr_ext < emaglim
        );
      })
      .map((x) => {
        const phase = (x.mjd % period) / period;
        return [
          phase,
          x.mag_corr,
          x.candid !== undefined ? x.candid : x.objectid,
          x.e_mag_corr_ext,
          x.isdiffpos !== undefined ? x.isdiffpos : x.field,
        ];
      });
    const folded2 = folded1.map((x) => {
      return [x[0] + 1, x[1], x[2], x[3], x[4]];
    });
    return folded1.concat(folded2);
  }

  formatError(detections, band, period, forced = false, flux = false) {
    const maglim = flux ? 999999 : 99;
    const emaglim = flux ? 999999 : 1;
    const errors1 = detections
      .filter(function (x) {
        if (forced && "extra_fields" in x) {
          if ("distnr" in x["extra_fields"]) {
            return (
              x["extra_fields"]["distnr"] >= 0 &&
              x.fid === band &&
              x.corrected &&
              x.e_mag_corr_ext < emaglim &&
              x.mag_corr > 0 &&
              x.mag_corr <= maglim
            );
          }
          return (
            x.fid === band &&
            x.corrected &&
            x.e_mag_corr_ext < emaglim &&
            x.mag_corr > 0 &&
            x.mag_corr <= maglim
          );
        }
        return (
          x.fid === band &&
          x.corrected &&
          x.mag_corr != null &&
          x.mag_corr > 0 &&
          x.mag_corr <= maglim &&
          x.e_mag_corr_ext < emaglim
        );
      })
      .map(function (x) {
        const phase = (x.mjd % period) / period;
        return [
          phase,
          x.mag_corr - x.e_mag_corr_ext,
          x.mag_corr + x.e_mag_corr_ext,
        ];
      });

    const errors2 = errors1.map((x) => {
      if (x[0] === null) {
        return x;
      }
      return [x[0] + 1, x[1], x[2]];
    });
    return errors1.concat(errors2);
  }

  getLegend() {
    let legend = this.options.series
      .filter((x) => x.data.length > 0)
      .map((x) => x.name);
    this.options.legend.data = legend;
    this.options.title.subtext = "Period: " + this.period.toFixed(6) + " days";
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

  lcFoldedOnClick(detection) {
    const date = jdToDate(detection.value[0]).toUTCString().slice(0, -3) + "UT";
    return {
      mjd: detection.value[0],
      date,
      index: this.detections.findIndex((x) => x.mjd === detection.value[0]),
    };
  }
}

import { jdToDate } from './astro-dates.js'
import { LightCurveOptions } from './lc-utils.js'

export class ApparentLightCurveOptions extends LightCurveOptions {
  constructor(detections, nonDetections, fontColor) {
    super(detections, nonDetections, fontColor)
    this.detections = this.detections.filter(
      (x) => x.mag_corr <= 23 && x.e_mag_corr_ext < 1
    )

    this.getSeries()
    this.getLegend()
    this.getBoundaries()
  }

  getSeries() {
    const bands = new Set(this.detections.map((item) => item.fid))
    this.addDetections(this.detections, bands)
    this.addErrorBars(this.detections, bands)
  }

  addDetections(detections, bands) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name,
        type: 'scatter',
        scale: true,
        color: this.bandMap[band].color,
        symbolSize: 6,
        encode: {
          x: 0,
          y: 1,
        },
      }
      serie.data = this.formatDetections(detections, band)
      this.options.series.push(serie)
    })
  }

  addErrorBars(detections, bands) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name,
        type: 'custom',
        scale: true,
        color: this.bandMap[band].color,
        renderItem: this.renderError,
      }
      serie.data = this.formatError(detections, band)
      this.options.series.push(serie)
    })
  }

  formatError(detections, band) {
    return detections
      .filter(function (x) {
        return x.fid === band && x.corrected
      })
      .map(function (x) {
        return [
          x.mjd,
          x.mag_corr - x.e_mag_corr_ext,
          x.mag_corr + x.e_mag_corr_ext,
        ]
      })
  }

  formatDetections(detections, band) {
    return detections
      .filter(function (x) {
        return x.fid === band && x.corrected
      })
      .map(function (x) {
        return [
          x.mjd,
          x.mag_corr,
          x.candid,
          x.e_mag_corr_ext,
          x.isdiffpos,
        ]
      })
  }

  getLegend() {
    const bands = Array.from(new Set(this.detections.map((item) => item.fid)))
    const legend = bands.map((band) => this.bandMap[band].name)
    this.options.legend.data = legend
  }

  getBoundaries() {
    const sigmas = this.detections.map((x) => x.e_mag_corr_ext)
    const maxSigma = Math.max.apply(Math, sigmas) + 0.1
    this.options.yAxis.min = (x) => (x.min - maxSigma).toFixed(1)
    this.options.yAxis.max = (x) => (x.max + maxSigma).toFixed(1)
  }

  lcApparentOnClick(detection) {
    console.log(detection);
    const date = jdToDate(detection.value[0]).toUTCString().slice(0, -3) + 'UT'
    return {
      mjd: detection.value[0],
      date,
      index: this.detections.findIndex((x) => x.mjd === detection.value[0]),
    }
  }
}
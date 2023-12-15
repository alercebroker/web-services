import { LightCurveOptions } from './lc-utils.js'

export class FoldedLightCurveOptions extends LightCurveOptions {
  constructor(detections, nonDetections, fontColor, period) {
    super(detections, nonDetections, fontColor)
    this.detections = this.detections.filter(
      (x) => x.mag_corr <= 23 && x.e_mag_corr_ext < 1
    )
    this.period = period
    this.getSeries()
    this.getLegend()
    this.getBoundaries()
  }

  getSeries(data) {
    const bands = Array.from(new Set(this.detections.map((item) => item.fid)))
    this.addDetections(this.detections, bands, this.period)
    this.addErrorBars(this.detections, bands, this.period)
  }

  addDetections(detections, bands, period) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name,
        type: 'scatter',
        scale: true,
        color: this.bandMap[band].color,
        symbolSize: band < 100 ? 6 : 3,
        symbol: band < 100 ? 'circle' : 'square',
        encode: {
          x: 0,
          y: 1,
        },
        zlevel: band < 100 ? 10 : 0,
      }
      serie.data = this.formatDetections(detections, band, period)
      this.options.series.push(serie)
    })
  }

  addErrorBars(detections, bands, period) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name,
        type: 'custom',
        scale: true,
        color: this.bandMap[band].color,
        renderItem: this.renderError,
      }
      serie.data = this.formatError(detections, band, period)
      this.options.series.push(serie)
    })
  }

  formatDetections(detections, band, period) {
    const folded1 = detections
      .filter((x) => x.fid === band && x.corrected)
      .map((x) => {
        const phase = (x.mjd % period) / period
        return [
          phase,
          x.mag_corr,
          x.candid,
          x.e_mag_corr_ext,
          x.isdiffpos,
        ]
      })
    const folded2 = folded1.map((x) => {
      return [x[0] + 1, x[1], x[2], x[3], x[4]]
    })
    return folded1.concat(folded2)
  }

  formatError(detections, band, period) {
    const errors1 = detections
      .filter(function (x) {
        return (
          x.fid === band &&
          x.corrected &&
          x.mag_corr != null &&
          x.mag_corr < 100
        )
      })
      .map(function (x) {
        const phase = (x.mjd % period) / period
        return [
          phase,
          x.mag_corr - x.e_mag_corr_ext,
          x.mag_corr + x.e_mag_corr_ext,
        ]
      })

    const errors2 = errors1.map((x) => {
      if (x[0] === null) {
        return x
      }
      return [x[0] + 1, x[1], x[2]]
    })
    return errors1.concat(errors2)
  }

  getLegend() {
    let bands = Array.from(new Set(this.detections.map((item) => item.fid)))
    bands = bands.sort((x, y) => x - y)
    let legend = bands.map((band) => this.bandMap[band].name)
    legend = legend.concat(
      bands.map((band) => this.bandMap[band].name + ' detections')
    )
    this.options.legend.data = legend
    this.options.title.subtext = 'Period: ' + this.period.toFixed(6) + ' days'
  }

  getBoundaries() {
    const sigmas = this.detections.map((x) => x.e_mag_corr_ext)
    const maxSigma = Math.max.apply(Math, sigmas) + 0.1
    this.options.yAxis.min = (x) => (x.min - maxSigma).toFixed(1)
    this.options.yAxis.max = (x) => (x.max + maxSigma).toFixed(1)
  }

  lcFoldedOnClick(detection) {
    console.log(detection);
    const date = jdToDate(detection.value[0]).toUTCString().slice(0, -3) + 'UT'
    return {
      mjd: detection.value[0],
      date,
      index: this.detections.findIndex((x) => x.mjd === detection.value[0]),
    }
  }
}
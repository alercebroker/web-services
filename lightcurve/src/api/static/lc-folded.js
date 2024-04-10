import { LightCurveOptions } from './lc-utils.js'

export class FoldedLightCurveOptions extends LightCurveOptions {
  constructor(detections, forcedPhotometry, fontColor, period) {
    super(detections, [], forcedPhotometry, fontColor, "Folded Light Curve")
    this.detections = detections
    this.forcedPhotometry = forcedPhotometry
    this.period = period
    this.getSeries()
    this.getLegend()
    this.getBoundaries()
  }

  getSeries(data) {
    const bands = Array.from(new Set(this.detections.map((item) => item.fid)))
    const fpBands = Array.from(new Set(this.forcedPhotometry.map((item) => item.fid)))
    this.addDetections(this.detections, bands, this.period)
    this.addErrorBars(this.detections, bands, this.period)
    this.addForcedPhotometry(this.forcedPhotometry, fpBands, this.period)
    this.addErrorBarsForcedPhotometry(this.forcedPhotometry, fpBands, this.period)
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

  addForcedPhotometry(detections, bands, period) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name + ' forced photometry',
        type: 'scatter',
        scale: true,
        color: this.bandMap[band].color,
        symbolSize: 6,
        symbol: 'square',
        encode: {
          x: 0,
          y: 1,
        },
        zlevel: 10,
      }
      serie.data = this.formatForcedPhotometry(detections, band, period)
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

  addErrorBarsForcedPhotometry(detections, bands, period) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name + ' forced photometry',
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
    .filter((x) => x.fid === band && x.corrected && x.mag_corr > 0 && x.mag_corr < 100 && x.e_mag_corr_ext < 1)
      .map((x) => {
        const phase = (x.mjd % period) / period
        return [
          phase,
          x.mag_corr,
          x.candid !== undefined ? x.candid : x.objectid,
          x.e_mag_corr_ext,
          x.isdiffpos !== undefined ? x.isdiffpos : x.field,
        ]
      })
    const folded2 = folded1.map((x) => {
      return [x[0] + 1, x[1], x[2], x[3], x[4]]
    })
    return folded1.concat(folded2)
  }

  formatForcedPhotometry(detections, band, period) {
    const folded1 = detections
      .filter((x) => {
        if ('distnr' in x['extra_fields']) {
          return (
            x['extra_fields']['distnr'] >= 0 && 
            x.fid === band && 
            x.corrected &&
            x.mag_corr > 0 &&
            x.mag_corr < 100 &&
            x.e_mag_corr_ext < 1
          )
        }
        return (
          x.fid === band && 
          x.corrected &&
          x.mag_corr > 0 &&
          x.mag_corr < 100 &&
          x.e_mag_corr_ext < 1
        )
      })
      .map((x) => {
        const phase = (x.mjd % period) / period
        return [
          phase,
          x.mag_corr,
          x.candid !== undefined ? x.candid : x.objectid,
          x.e_mag_corr_ext,
          x.isdiffpos !== undefined ? x.isdiffpos : x.field,
        ]
      })
    const folded2 = folded1.map((x) => {
      return [x[0] + 1, x[1], x[2], x[3], x[4]]
    })
    return folded1.concat(folded2)
  }

  formatError(detections, band, period, forced = false) {
    const errors1 = detections
      .filter(function (x) {
        if (forced) {
          if ('distnr' in x['extra_fields']) {
            return (
              x['extra_fields']['distnr'] >= 0 &&
              x.fid === band &&
              x.corrected &&
              x.e_mag_corr_ext < 1 &&
              x.mag_corr > 0 &&
              x.mag_corr < 100
            )
          }
          return (
            x.fid === band &&
            x.corrected &&
            x.e_mag_corr_ext < 1 &&
            x.mag_corr > 0 &&
            x.mag_corr < 100
          )
        }
        return (
          x.fid === band &&
          x.corrected &&
          x.mag_corr != null &&
          x.mag_corr > 0 &&
          x.mag_corr < 100 &&
          x.e_mag_corr_ext < 1
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
    legend = legend.concat(
      bands.map((band) => this.bandMap[band].name + ' forced photometry')
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

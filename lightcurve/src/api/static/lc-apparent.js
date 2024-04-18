import { jdToDate } from './astro-dates.js'
import { LightCurveOptions } from './lc-utils.js'

export class ApparentLightCurveOptions extends LightCurveOptions {
  constructor(detections, forcedPhotometry, fontColor, flux=false) {
    super(detections, [], forcedPhotometry, fontColor, "Apparent Magnitude")
    this.detections = detections
    this.forcedPhotometry = forcedPhotometry
    this.getSeries(flux)
    this.getLegend()
    this.getBoundaries()
  }

  getSeries(flux) {
    const bands = new Set(this.detections.map((item) => item.fid))
    const fpBands = new Set(this.forcedPhotometry.map((item) => item.fid))
    let detections = this.detections
    let forcedPhotometry = this.forcedPhotometry
    if (flux) {
      detections = LightCurveOptions.magToFlux(this.detections, true)
      forcedPhotometry = LightCurveOptions.magToFlux(this.forcedPhotometry, true)
      this.options.yAxis.inverse = false
      this.options.yAxis.name = 'Flux [uJy]'
      this.options.yAxis.nameLocation = 'end'
      this.options.title.text = "Total Flux"
    }
    this.addDetections(detections, bands, flux)
    this.addErrorBars(detections, bands, flux)
    this.addForcedPhotometry(forcedPhotometry, fpBands, flux)
    this.addErrorBarsForcedPhotometry(forcedPhotometry, fpBands, flux)
  }

  addDetections(detections, bands, flux) {
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
      serie.data = this.formatDetections(detections, band, flux)
      this.options.series.push(serie)
    })
  }

  addForcedPhotometry(detections, bands, flux) {
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
        zlevel: band < 100 ? 10 : 0,
      }
      serie.data = this.formatForcedPhotometry(detections, band, flux)
      this.options.series.push(serie)
    })
  }

  addErrorBars(detections, bands, flux) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name,
        type: 'custom',
        scale: true,
        color: this.bandMap[band].color,
        renderItem: this.renderError,
      }
      serie.data = this.formatError(detections, band, flux)
      this.options.series.push(serie)
    })
  }

  addErrorBarsForcedPhotometry(forcedPhotometry, bands, flux) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name + ' forced photometry',
        type: 'custom',
        scale: true,
        color: this.bandMap[band].color,
        renderItem: this.renderError,
      }
      serie.data = this.formatError(forcedPhotometry, band, true, flux)
      this.options.series.push(serie)
    })
  }

  formatError(detections, band, forced=false, flux=false) {
    return detections
      .filter(function (x) {
        const magLimit = flux ? 999999 : 99
        if (forced && 'extra_fields' in x) {
          if ('distnr' in x['extra_fields']) {
            return x['extra_fields']['distnr'] >= 0 && x.fid === band && x.corrected && x.e_mag_corr_ext < 99 && x.mag_corr > 0 && x.mag_corr <= magLimit
          }
          return x.fid === band && x.corrected && x.e_mag_corr_ext < 99 && x.mag_corr > 0 && x.mag_corr <= magLimit
        }
        return x.fid === band && x.corrected && x.e_mag_corr_ext < 99 && x.mag_corr > 0 && x.mag_corr <= magLimit
      })
      .map(function (x) {
        return [
          x.mjd,
          x.mag_corr - x.e_mag_corr_ext,
          x.mag_corr + x.e_mag_corr_ext,
        ]
      })
  }

  formatDetections(detections, band, flux) {
    return detections
      .filter(function (x) {
        const magLimit = flux ? 999999 : 99
        return x.fid === band && x.corrected && x.mag_corr > 0 && x.mag_corr <= magLimit && x.e_mag_corr_ext < 99
      })
      .map(function (x) {
        return [
          x.mjd,
          x.mag_corr,
          x.candid !== undefined ? x.candid : x.objectid,
          x.e_mag_corr_ext,
          x.isdiffpos !== undefined ? x.isdiffpos : x.field,
        ]
      })
  }

  formatForcedPhotometry(forcedPhotometry, band, flux) {
    const magLim = flux ? 999999 : 99
    return forcedPhotometry
      .filter(function (x) {
        if ('extra_fields' in x) {
          if ('distnr' in x['extra_fields']) {
            return x['extra_fields']['distnr'] >= 0 && x.fid === band && x.corrected && x.mag_corr > 0 && x.mag_corr <= magLim && x.e_mag_corr_ext < 99
          }
        }
        return x.fid === band && x.corrected && x.mag_corr > 0 && x.mag_corr <= magLim && x.e_mag_corr_ext < 99
      })
      .map(function (x) {
        return [x.mjd, x.mag_corr, 'no-candid', x.e_mag_corr_ext, x.isdiffpos]
      })
  }

  getLegend() {
    let bands = Array.from(new Set(this.detections.map((item) => item.fid)))
    bands = bands.sort((x, y) => x - y)
    let legend = bands.map((band) => this.bandMap[band].name)
    legend = legend.concat(
      bands.map((band) => this.bandMap[band].name + ' forced photometry')
    )
    this.options.legend.data = legend
  }

  getBoundaries() {
    const sigmas = this.detections.concat(this.forcedPhotometry).map((x) => x.e_mag_corr_ext)
    const maxSigma = sigmas.reduce((a, b) => Math.max(a, b), -Infinity)
    this.options.yAxis.min = (x) => (x.min - maxSigma).toFixed(1)
    this.options.yAxis.max = (x) => (x.max + maxSigma).toFixed(1)
  }

  lcApparentOnClick(detection) {
    const date = jdToDate(detection.value[0]).toUTCString().slice(0, -3) + 'UT'
    return {
      mjd: detection.value[0],
      date,
      index: this.detections.findIndex((x) => x.mjd === detection.value[0]),
    }
  }
}

import { jdToDate } from './astro-dates.js'
import { LightCurveOptions } from './lc-utils.js'


export class DifferenceLightCurveOptions extends LightCurveOptions {
  constructor(detections, nonDetections, forcedPhotometry, fontColor, flux=false) {
    super(detections, nonDetections, forcedPhotometry, fontColor, "Difference Magnitude")
    if (flux) {
      this.detections = LightCurveOptions.magToFlux(detections)
    } else {
      this.detections = detections
    }
    this.nonDetections = nonDetections
    this.forcedPhotometry = forcedPhotometry
    this.getSeries()
    this.getLegend()
    this.getBoundaries()
  }

  getSeries() {
    const bands = new Set(this.detections.map((item) => item.fid))
    const ndBands = new Set(this.nonDetections.map((item) => item.fid))
    const fpBands = new Set(this.forcedPhotometry.map((item) => item.fid))
    this.addDetections(this.detections, bands)
    this.addErrorBars(this.detections, bands)
    this.addNonDetections(this.nonDetections, ndBands)
    this.addForcedPhotometry(this.forcedPhotometry, fpBands)
    this.addErrorBarsForcedPhotometry(this.forcedPhotometry, fpBands)
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

  addErrorBarsForcedPhotometry(forcedPhotometry, bands) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name + ' forced photometry',
        type: 'custom',
        scale: true,
        color: this.bandMap[band].color,
        renderItem: this.renderError,
      }
      serie.data = this.formatError(forcedPhotometry, band)
      this.options.series.push(serie)
    })
  }

  addNonDetections(nonDetections, bands) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name + ' non-detections',
        type: 'scatter',
        scale: true,
        color: this.hexToRGB(this.bandMap[band].color, 0.5),
        symbolSize: 6,
        symbol:
          'path://M0,49.017c0-13.824,11.207-25.03,25.03-25.03h438.017c13.824,0,25.029,11.207,25.029,25.03L262.81,455.745c0,0-18.772,18.773-37.545,0C206.494,436.973,0,49.017,0,49.017z',
      }
      serie.data = this.formatNonDetections(nonDetections, band)
      this.options.series.push(serie)
    })
  }

  addForcedPhotometry(forcedPhotometry, bands) {
    bands.forEach((band) => {
      const serie = {
        name: this.bandMap[band].name + ' forced photometry',
        type: 'scatter',
        scale: true,
        color: this.bandMap[band].color,
        symbolSize: 6,
        symbol: 'path://M0,0 L0,10 L10,10 L10,0 Z',
        encode: {
          x: 0,
          y: 1,
        },
      }
      serie.data = this.formatForcedPhotometry(forcedPhotometry, band)
      this.options.series.push(serie)
    })
  }

  formatError(detections, band) {
    return detections
      .filter(function (x) {
        return x.fid === band && x.e_mag < 100
      })
      .map(function (x) {
        return [x.mjd, x.mag - x.e_mag, x.mag + x.e_mag]
      })
  }

  formatDetections(detections, band) {
    return detections
      .filter(function (x) {
        return x.fid === band && x.mag <= 24
      })
      .map(function (x) {
        return [x.mjd, x.mag, x.candid, x.e_mag, x.isdiffpos]
      })
  }

  formatForcedPhotometry(forcedPhotometry, band) {
    return forcedPhotometry
      .filter(function (x) {
        if ("distnr" in x["extra_fields"]) {
          return x["extra_fields"]["distnr"] >= 0 && x.fid === band && x.mag <= 24
        }
        return x.fid === band && x.mag <= 24
      })
      .map(function (x) {
        return [x.mjd, x.mag, "no-candid", x.e_mag, x.isdiffpos]
      })
  }

  formatNonDetections(nonDetections, band) {
    return nonDetections
      .filter(function (x) {
        return x.fid === band && x.diffmaglim > 10 && x.diffmaglim <= 23
      })
      .map(function (x) {
        return [x.mjd, x.diffmaglim]
      })
  }

  getLegend() {
    let bands = Array.from(new Set(this.detections.map((item) => item.fid)))
    bands = bands.sort((x, y) => x - y)
    let legend = bands.map((band) => this.bandMap[band].name)
    legend = legend.concat(
      bands.map((band) => this.bandMap[band].name + ' non-detections')
    )
    legend = legend.concat(
      bands.map((band) => this.bandMap[band].name + ' forced photometry')
    )
    this.options.legend.data = legend
  }

  getBoundaries() {
    const sigmas = this.detections.map((x) => x.e_mag)
    const maxSigma = Math.max.apply(Math, sigmas) + 0.1
    this.options.yAxis.min = (x) => (x.min - maxSigma).toFixed(1)
    this.options.yAxis.max = (x) => (x.max + maxSigma).toFixed(1)
  }

  lcDifferenceOnClick(detection) {
    console.log(detection);
    const date = jdToDate(detection.value[0]).toUTCString().slice(0, -3) + 'UT'
    return {
      mjd: detection.value[0],
      date,
      index: this.detections.findIndex((x) => x.mjd === detection.value[0]),
    }
  }
}

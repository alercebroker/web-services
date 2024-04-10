import { jdToDate } from './astro-dates.js'

export class LightCurveOptions {
  constructor(detections = [], nonDetections = [], forcedPhotometry = [], fontColor = 'fff', title = 'Light Curve') {
    this.bandMap = {
      1: { name: 'g', color: '#56E03A' },
      2: { name: 'r', color: '#D42F4B' },
      3: { name: 'i', color: '#F4D617' },
      101: { name: 'g DR5', color: '#ADA3A3' },
      102: { name: 'r DR5', color: '#377EB8' },
      103: { name: 'i DR5', color: '#FF7F00' },
      4: { name: 'c', color: '#00FFFF' },
      5: { name: 'o', color: '#FFA500' },
    }
    this.fontColor = fontColor
    this.options = {
      grid: {
        left: '7%',
        right: '5%',
      },
      title: {
        text: title,
        left: 'center',
        textStyle: {
          fontWeight: 'lighter',
          color: this.fontColor,
        },
      },
      tooltip: {
        show: true,
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: '#505765',
          },
        },
        formatter: this.formatTooltip,
      },
      toolbox: {
        show: true,
        showTitle: true,
        feature: {
          dataZoom: {
            show: true,
            title: {
              zoom: 'Zoom',
              back: 'Back',
            },
            icon: {
              zoom:
                'M11,4A7,7 0 0,1 18,11C18,12.5 17.5,14 16.61,15.19L17.42,16H18L23,21L21,23L16,18V17.41L15.19,16.6C12.1,18.92 7.71,18.29 5.39,15.2C3.07,12.11 3.7,7.72 6.79,5.4C8,4.5 9.5,4 11,4M10,7V10H7V12H10V15H12V12H15V10H12V7H10M1,1V8L8,1H1Z',
              back:
                'M21,11H6.83L10.41,7.41L9,6L3,12L9,18L10.41,16.58L6.83,13H21V11Z',
            },
          },
          restore: {
            show: true,
            title: 'Restore',
          },
        },
        tooltip: {
          formatter(param) {
            return '<div>' + param.title + '</div>' // user-defined DOM structure
          },
          backgroundColor: '#222',
          textStyle: {
            fontSize: 12,
          },
          extraCssText: 'box-shadow: 0 0 3px rgba(0, 0, 0, 0.3);', // user-defined CSS styles
        },
      },
      legend: {
        data: [], // ["g", "r", "g non-detections", "r non-detections", "g forced photometry", "r forced photometry"],
        bottom: 0,
        type: 'scroll',
        textStyle: {
          fontWeight: 'lighter',
          color: this.fontColor,
        },
      },
      xAxis: {
        name: 'Modified Julian Dates',
        nameLocation: 'center',
        scale: true,
        type: 'value',
        splitLine: {
          show: false,
        },
        nameTextStyle: {
          padding: 7,
        },
      },
      yAxis: {
        name: 'Magnitude',
        nameLocation: 'start',
        type: 'value',
        scale: true,
        splitLine: {
          show: false,
        },
        inverse: true,
        min: 15,
        max: 25,
      },
      textStyle: {
        color: this.fontColor,
        fontWeight: 'lighter',
      },
      series: [],
    }
  }

  /**
   * Sets options legend from data
   */
  getLegend() {
    throw new Error("Method 'getLegend()' must be implemented")
  }

  /**
   * Sets options series from data
   */
  getSeries() {
    throw new Error("Method 'getSeries()' must be implemented")
  }

  formatTooltip(params) {
    const colorSpan = (color) =>
      '<span style="display:inline-block;margin-right:5px;border-radius:10px;width:9px;height:9px;background-color:' +
      color +
      '"></span>'
    const rowTable = (col1, col2, col3) =>
      '<tr> <td>' +
      col1 +
      '</td> <td>' +
      col2 +
      '</td> <td>' +
      col3 +
      '</td> </tr>'
    const dataReleaseTooltip = (params) => {
      const color = params.color
      const mjd = params.value[0]
      const mag = params.value[1].toFixed(3)
      const objectid = params.value[2]
      const magerr = params.value[3].toFixed(3)
      const field = params.value[4]
      const magnitude = `${mag} ± ${magerr}`
      const utcDate = jdToDate(mjd).toUTCString().slice(0, -3) + 'UT'
      let data = ''
      data += rowTable('', 'objectid: ', objectid)
      data += rowTable('', 'field: ', field)
      data += rowTable(colorSpan(color), `${params.seriesName}: `, magnitude)
      data += rowTable(calendarIcon(color), 'MJD: ', mjd)
      data += rowTable(calendarIcon(color), 'Date: ', utcDate)
      return data
    }
    const calendarIcon = (color) =>
      `<span class="mdi mdi-alarm" style='font-size:13px; color: ${color};'></span>`
    const serie = params[0].seriesName
    let table = '<table> <tr> <th></th> <th></th> <th></th></tr>'
    if (serie === 'r non-detections' || serie === 'g non-detections') {
      table += rowTable(
        colorSpan(params[0].color),
        params[0].seriesName + ':',
        params[0].value[1]
      )
      table += rowTable(
        calendarIcon(params[0].color),
        'MJD: ',
        params[0].value[0]
      )
      table += rowTable(
        calendarIcon(params[0].color),
        'Date: ',
        jdToDate(params[0].value[0]).toUTCString().slice(0, -3) + 'UT'
      )
      return table + '</table>'
    } else if (serie === 'r' || serie === 'g') {
      const isdiffpos = params[0].value[4] === 1 ? '(+)' : '(-)'
      const mag = params[0].value[1].toFixed(3)
      const err = params[0].value[3].toFixed(3)
      table += rowTable('', 'candid: ', params[0].value[2])
      table += rowTable(
        colorSpan(params[0].color),
        params[0].seriesName + ': ',
        `${isdiffpos} ${mag} ± ${err}`
      )
      table += rowTable(
        calendarIcon(params[0].color),
        'MJD: ',
        params[0].value[0]
      )
      table += rowTable(
        calendarIcon(params[0].color),
        'Date: ',
        jdToDate(params[0].value[0]).toUTCString().slice(0, -3) + 'UT'
      )
      table += rowTable('', 'click to change stamp', '')
      return table + '</table>'
    } else if (serie === 'r DR5' || serie === 'g DR5' || serie === 'i DR5') {
      table += dataReleaseTooltip(params[0])
      return table
    } else if (serie === 'r forced photometry' || serie === 'g forced photometry') {
      const isdiffpos = params[0].value[4] === 1 ? '(+)' : '(-)'
      const mag = params[0].value[1].toFixed(3)
      const err = params[0].value[3].toFixed(3)
      table += rowTable(
        colorSpan(params[0].color),
        params[0].seriesName + ': ',
        `${isdiffpos} ${mag} ± ${err}`
      )
      table += rowTable(
        calendarIcon(params[0].color),
        'MJD: ',
        params[0].value[0]
      )
      table += rowTable(
        calendarIcon(params[0].color),
        'Date: ',
        jdToDate(params[0].value[0]).toUTCString().slice(0, -3) + 'UT'
      )
      return table + '</table>'
    }
  }

  renderError(params, api) {
    const xValue = api.value(0)
    const highPoint = api.coord([xValue, api.value(1)])
    const lowPoint = api.coord([xValue, api.value(2)])
    const halfWidth = 1.9 // api.size([1, 0])[0] * 0.1
    const style = api.style({
      stroke: api.visual('color'),
      fill: null,
    })
    return {
      type: 'group',
      children: [
        {
          type: 'line',
          shape: {
            x1: highPoint[0] - halfWidth,
            y1: highPoint[1],
            x2: highPoint[0] + halfWidth,
            y2: highPoint[1],
          },
          style,
        },
        {
          type: 'line',
          shape: {
            x1: highPoint[0],
            y1: highPoint[1],
            x2: lowPoint[0],
            y2: lowPoint[1],
          },
          style,
        },
        {
          type: 'line',
          shape: {
            x1: lowPoint[0] - halfWidth,
            y1: lowPoint[1],
            x2: lowPoint[0] + halfWidth,
            y2: lowPoint[1],
          },
          style,
        },
      ],
    }
  }

  hexToRGB(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16)
    const g = parseInt(hex.slice(3, 5), 16)
    const b = parseInt(hex.slice(5, 7), 16)

    if (alpha) {
      return 'rgba(' + r + ', ' + g + ', ' + b + ', ' + alpha + ')'
    } else {
      return 'rgb(' + r + ', ' + g + ', ' + b + ')'
    }
  }
}

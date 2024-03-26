export class PeriodogramOptions {
  constructor(detections = [], fontColor = 'fff') {
    this.detections = detections;
    this.fontColor = fontColor;

    this.options = {
      grid: {
        left: '7%',
        right: '5%',
        bottom: '20%',
        containLabel: true,
      },
      title: {
        text: 'Periodogram',
        left: 'center',
        textStyle: {
          fontWeight: 'lighter',
          color: this.fontColor,
        },
      },
      legend: {
        type: "plain",
        show: true
      },
      tooltip: {
        show: true,
        trigger: 'item',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: '#505765',
          },
        },
        formatter: (params) => {
          return `<b>Period:</b> ${params[0].data[0]} <b>Score:</b> ${params[0].data[1]}`;
        }
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
      },
      xAxis: {
        name: "Period",
        type: "value",
        type: "log",
        scale: true,
        splitLine: {
          show: false,
        },
        min: 0.05,
        max: 500,
      },
      yAxis: {
        name: "Score",
        type: "value",
        nameLocation: 'end',
        scale: true,
        splitLine: {
          show: false,
        },
      },
      textStyle: {
        color: this.fontColor,
        fontWeight: 'lighter',
      },
      animation: false,
      series: [
        {
          name: "Periods",
          type: "scatter",
          symbolSize: 5,
          animation: false,
          large: true,
          dimensions: [
            { name: "period", type: "float", displayName: "Period" },
            { name: "score", type: "float", displayName: "Score" }
          ],
          datasetIndex: 0,
          tooltip: {
            show: true,
            trigger: 'item',
            axisPointer: {
              type: 'cross',
              label: {
                backgroundColor: '#505765',
              },
            },
            formatter: (params) => {
              return `<b>Period:</b> ${params.data[0]} <b>Score:</b> ${params.data[1]}`;
            }
          },
        },
        {
          name: "Best periods",
          type: "scatter", 
          symbol: "triangle",
          color: "red",
          symbolSize: 10,
          animation: false,
          large: true,
          dimensions: [
            { name: "period", type: "float", displayName: "Period" },
            { name: "score", type: "float", displayName: "Score" }
          ],
          datasetIndex: 1,
          tooltip: {
            show: true,
            trigger: 'item',
            axisPointer: {
              type: 'cross',
              label: {
                backgroundColor: '#505765',
              },
            },
            formatter: (params) => {
              return `<b>Period:</b> ${params.data[0]} <b>Score:</b> ${params.data[1]}`;
            }
          },
        }
      ],
      dataset: [
        {
          dimensions: [
            { name: "period", type: "float", displayName: "Period" },
            { name: "score", type: "float", displayName: "Score" }
          ],
        },
        {
          dimensions: [
            { name: "period", type: "float", displayName: "Period" },
            { name: "score", type: "float", displayName: "Score" }
          ],
        },
      ]
    };
  }

  addSeries(periodogram) {
    const periods = {
      period: periodogram.period,
      score: periodogram.score
    }
    const best_periods = {
      period: periodogram.best_periods,
      score: periodogram.best_periods_index.map((idx) => periodogram.score[idx])
    }
    this.options.dataset[0].source = periods;
    this.options.dataset[1].source = best_periods;
  }
}
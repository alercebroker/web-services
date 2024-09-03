import { PeriodogramOptions } from "./periodogram/chartOptions.js";
import { linear_to_log, log_to_linear } from "./periodogram/utils.js";
import * as echarts from "./echarts.min.js";

export class Periodogram {
  constructor(period, detections, elements, apiUrl, refreshLightcurvePlot) {
    this.data = this.parseDetections(detections);
    this.apiUrl = apiUrl;
    this.refreshLightcurvePlot = refreshLightcurvePlot;

    this.chartOptions = new PeriodogramOptions();

    this.isPeriodogramBuilt = false;
    this.onSetPeriod = () => {};

    this.elements = elements;
    this.setPeriod(period);
    this.addListeners();
  }

  parseDetections(detections) {
    const fid_map = { 1: "g", 2: "r" };
    const detections_clean = detections.filter(
      (detection) =>
        detection.mjd !== null &&
        detection.mag_corr !== null &&
        detection.e_mag_corr_ext !== null &&
        (detection.fid === 1 || detection.fid === 2),
    );
    return {
      mjd: detections_clean.map((detection) => detection.mjd),
      brightness: detections_clean.map((detection) => detection.mag_corr),
      e_brightness: detections_clean.map(
        (detection) => detection.e_mag_corr_ext,
      ),
      fid: detections_clean.map((detection) => fid_map[detection.fid]),
    };
  }

  updateColorScheme(color_scheme) {
    let color = "#000";
    if (color_scheme === "tw-light") {
      color = "#000";
    } else if (color_scheme === "tw-dark") {
      color = "#fff";
    }

    let options = {
      title: { textStyle: { color } },
      textStyle: { color },
      legend: { textStyle: { color } },
    };

    if (this.isPeriodogramBuilt) this.periodogram_plot.setOption(options);
    else this.chartOptions = new PeriodogramOptions(color);
  }

  load() {
    if (this.isPeriodogramBuilt) return;

    this.periodogram_plot = echarts.init(this.elements.main);
    window.addEventListener("resize", this.periodogram_plot.resize);
    this.periodogram_plot.on("click", (params) => {
      this.setPeriod(params.data[0]);
    });

    this.elements.spiner.hidden = false;
    fetch(`${this.apiUrl}/period/compute_periodogram/`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(this.data),
    })
      .then((res) => res.json())
      .then((periodogram) => {
        this.chartOptions.addSeries(periodogram);
        this.periodogram_plot.setOption(this.chartOptions.options, true);

        this.isPeriodogramBuilt = true;
        this.elements.spiner.hidden = true;

        this.elements.main.style.display =
          !this.elements.check.checked || !this.isPeriodogramBuilt
            ? "none"
            : "initial";

        this.periodogram_plot.resize();
      });
    // .catch(() => {
    //   // TODO: Error handling
    // });
  }

  setPeriod(newPeriod) {
    newPeriod = parseFloat(newPeriod);

    this.period = newPeriod;
    this.elements.slider.value = log_to_linear(newPeriod);
    this.elements.field.value = newPeriod;

    this.refreshLightcurvePlot();

    fetch(`${this.apiUrl}/period/chi_squared/`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ ...this.data, period: this.period }),
    }).catch(() => {
      // TODO: Error handling
    });

    this.onSetPeriod(newPeriod);
  }

  doublePeriod() {
    this.setPeriod(this.period * 2);
  }

  halvePeriod() {
    this.setPeriod(this.period / 2);
  }

  addListeners() {
    this.elements.doubleButton.addEventListener("click", () =>
      this.doublePeriod(),
    );
    this.elements.halfButton.addEventListener("click", () =>
      this.halvePeriod(),
    );
    /* Set up Download and Data release buttons */
    this.elements.check.addEventListener("click", () => {
      this.load();
      this.elements.main.style.display =
        !this.elements.check.checked || !this.isPeriodogramBuilt
          ? "none"
          : "initial";
      this.periodogram_plot.resize();
    });

    this.elements.slider.addEventListener("change", () =>
      this.setPeriod(linear_to_log(this.elements.slider.value)),
    );
    this.elements.field.addEventListener("change", () =>
      this.setPeriod(this.elements.field.value),
    );
  }
}

/**
 * lightcurve-app.js
 *
 * Client-side lightcurve chart builder. Replaces the server-side /htmx/config_change
 * round-trip: all chart updates (band toggles, magnitude/flux, fold, period, offsets,
 * etc.) happen entirely in the browser without sending data back to the server.
 *
 * Reads initial data from window.__LC_DATA__ embedded by the layout template.
 */

// Derive static base URL from this module's own URL so no server-injected value needed.
const _BASE = new URL('.', import.meta.url).href;

const { default: customDark } = await import(`${_BASE}echarts-theme/customDark.js`);
const { jdToDate } = await import(`${_BASE}AstroDates.js`);

const customDarkTheme = customDark();

// ─── Data & initial config ────────────────────────────────────────────────────
const {
    detections: rawDetections,
    nonDetections: rawNonDetections,
    forcedPhotometry: rawForcedPhotometry,
    periodogram: _initialPeriodogram,
    config: initialConfig,
} = window.__LC_DATA__;

// Periodogram data – populated lazily the first time the user enables fold mode.
let rawPeriodogram = _initialPeriodogram;

// Mutable config driven by the config panel controls.
let config = JSON.parse(JSON.stringify(initialConfig));

// ZTF Data-Release detections loaded on demand (external sources feature).
let drDetections = [];

// ─── Visual constants ─────────────────────────────────────────────────────────
const COLORS = {
    'ztf':    { g: '#56E03A', r: '#D42F4B', i: '#F4D617' },
    'lsst':   { u: '#56B4E9', g: '#009E73', r: '#D55E00', i: '#E69F00', z: '#CC79A7', y: '#0072B2' },
    'ztf dr': { g: '#ADA3A3', r: '#377EB8', i: '#FF7F00' },
    'empty':  { empty: '#00CBFF' },
};

const NDL_SYMBOL =
    'path://M0,49.017c0-13.824,11.207-25.03,25.03-25.03h438.017c13.824,0,25.029,' +
    '11.207,25.029,25.03L262.81,455.745c0,0-18.772,18.773-37.545,0C206.494,436.973,0,49.017,0,49.017z';

const SYMBOLS = {
    'ztf':    { det: 'circle',   'lim. mag': NDL_SYMBOL, 'f. phot': 'square' },
    'lsst':   { det: 'roundRect',                         'f. phot': 'diamond' },
    'ztf dr': { det: 'circle',   'lim. mag': NDL_SYMBOL, 'f. phot': 'square' },
    'empty':  { empty: 'none' },
};

// ─── Helpers ──────────────────────────────────────────────────────────────────
function bandName(item) {
    const bm = item.band_map;
    return bm[String(item.band)] ?? bm[item.band] ?? '?';
}

function phase(mjd, period) {
    return (mjd % period) / period;
}

function isDark() {
    return document.getElementById('main-app')?.classList.contains('tw-dark') ?? false;
}

function currentTheme() {
    return isDark() ? customDarkTheme : 'light';
}

// ─── Per-survey value extraction ─────────────────────────────────────────────
/**
 * Returns { y, err, sign } for a detection, or null if unrecognised survey.
 * Mirrors the Python flux2magnitude / magnitude2flux logic.
 */
function detectionPoint(det, cfg) {
    const survey = det.survey_id.toLowerCase();
    const { flux, total } = cfg;
    let y, err, sign;

    if (survey === 'ztf') {
        const mag = total ? det.magpsf_corr : det.magpsf;
        if (flux) {
            const rawF = Math.pow(10, -0.4 * (mag - 23.9));
            y = (total ? rawF : rawF * det.isdiffpos) * 1000;
            const errMag = total ? det.sigmapsf_corr_ext : det.sigmapsf;
            err = Math.abs(errMag) * Math.abs(y);
        } else {
            y = mag;
            err = total ? det.sigmapsf_corr_ext : det.sigmapsf;
        }
        sign = String(det.isdiffpos);

    } else if (survey === 'lsst') {
        const rawF    = total ? det.scienceFlux    : det.psfFlux;
        const rawFErr = total ? det.scienceFluxErr  : det.psfFluxErr;
        sign = rawF < 0 ? '-' : '+';
        const absF    = Math.abs(rawF);
        const absErr  = Math.abs(rawFErr);
        const magErr  = absF > 0 ? (2.5 * absErr) / (Math.LN10 * absF) : 0;
        if (flux) {
            y = rawF;
            err = Math.LN10 * Math.abs(y) / 2.5 * magErr;
        } else {
            let f = rawF;
            if (f < 0) { f = Math.abs(f); if (total) f = -f; }
            y   = f > 0 ? 31.4 - 2.5 * Math.log10(f) : 0;
            err = magErr;
        }

    } else if (survey === 'ztf dr') {
        if (flux) {
            y = Math.pow(10, -0.4 * (det.mag_corr - 23.9)) * 1000;
            err = Math.abs(det.e_mag_corr_ext) * Math.abs(y);
        } else {
            y = det.mag_corr;
            err = Math.abs(det.e_mag_corr_ext);
        }
        sign = y < 0 ? '-' : '+';

    } else {
        return null;
    }

    return { y, err: Math.abs(err), sign };
}

/**
 * Returns { y, err } for a forced-photometry point, or null.
 */
function forcedPhotPoint(fp, cfg) {
    const survey = fp.survey_id.toLowerCase();
    const { flux, total } = cfg;
    let y, err;

    if (survey === 'ztf') {
        const mag = total ? fp.mag_corr : fp.mag;
        if (flux) {
            y   = Math.pow(10, -0.4 * (mag - 23.9)) * 1000;
            err = Math.abs(total ? fp.e_mag_corr : fp.e_mag) * Math.abs(y);
        } else {
            y   = mag;
            err = Math.abs(total ? fp.e_mag_corr : fp.e_mag);
        }

    } else if (survey === 'lsst') {
        const rawF    = total ? fp.scienceFlux    : fp.psfFlux;
        const rawFErr = total ? fp.scienceFluxErr  : fp.psfFluxErr;
        const absF    = Math.abs(rawF);
        const absErr  = Math.abs(rawFErr);
        const magErr  = absF > 0 ? (2.5 * absErr) / (Math.LN10 * absF) : 0;
        if (flux) {
            y   = rawF;
            err = Math.LN10 * Math.abs(y) / 2.5 * magErr;
        } else {
            const f = rawF > 0 ? rawF : 0;
            y   = f > 0 ? 31.4 - 2.5 * Math.log10(f) : 0;
            err = magErr;
        }

    } else {
        return null;
    }

    return { y, err: Math.abs(err) };
}

// ─── Validity filter ──────────────────────────────────────────────────────────
function validPoint(y, surveyId, cfg) {
    const lsst = surveyId.toLowerCase() === 'lsst';
    if (cfg.flux) {
        const lim = lsst ? 9_999_999 : 999_999;
        return y > -lim && y < lim;
    }
    return y > 0 && y < 99;
}

// ─── ECharts series factories ─────────────────────────────────────────────────
function makeSeries(type, survey, band, data) {
    const sk = survey.toLowerCase();
    return {
        name:       `${type} ${survey.toUpperCase()}: ${band}`,
        type:       'scatter',
        data,
        color:      COLORS[sk]?.[band] ?? '#888888',
        symbol:     SYMBOLS[sk]?.[type]  ?? 'circle',
        symbolSize: 9,
        survey:     sk,
        z:          sk === 'ztf dr' ? 2 : 10,
        band,
    };
}

function makeErrorBarSeries(type, survey, band, errData) {
    const sk    = survey.toLowerCase();
    const color = COLORS[sk]?.[band] ?? '#888888';
    const name  = `${type} ${survey.toUpperCase()}: ${band}`;

    let minPt = null, maxPt = null;
    for (const p of errData) {
        if (!minPt || p[1] < minPt[1]) minPt = [p[0], p[1]];
        if (!maxPt || p[2] > maxPt[1]) maxPt = [p[0], p[2]];
    }

    return {
        name,
        type:       'scatter',
        data:       errData.map(p => [p[0], (p[1] + p[2]) / 2]),
        silent:     true,
        symbolSize: 0,
        color,
        markLine: {
            data: errData.map(p => [
                { coord: [p[0], p[1]], symbol: 'none' },
                { coord: [p[0], p[2]], symbol: 'none' },
            ]),
            lineStyle: { color, type: 'solid' },
        },
        error_bar:      true,
        min_plot_error: minPt,
        max_plot_error: maxPt,
        survey:         sk,
        band,
    };
}

// ─── Point grouping ───────────────────────────────────────────────────────────
function groupByBand(points) {
    const g = {};
    for (const { survey, band, pt } of points) {
        (g[survey] ??= {})[band] ??= [];
        g[survey][band].push(pt);
    }
    return g;
}

function groupedToSeries(type, grouped, grouped_err) {
    const out = [];
    for (const [surv, bands] of Object.entries(grouped)) {
        for (const [band, data] of Object.entries(bands)) {
            out.push(makeSeries(type, surv, band, data));
        }
    }
    for (const [surv, bands] of Object.entries(grouped_err)) {
        for (const [band, data] of Object.entries(bands)) {
            out.push(makeErrorBarSeries(type, surv, band, data));
        }
    }
    return out;
}

// ─── Series builders ──────────────────────────────────────────────────────────
function buildDetectionSeries(cfg) {
    if (!(cfg.data_types ?? ['detections']).includes('detections')) return [];
    const all     = [...rawDetections, ...(cfg.external_sources?.enabled ? drDetections : [])];
    const maxErr  = cfg.flux ? 99_999 : 1;
    const pts     = [], errPts = [];

    for (const det of all) {
        const survey = det.survey_id.toLowerCase();
        const bn     = bandName(det);

        if (survey === 'ztf'    && !cfg.bands.ztf.includes(bn))    continue;
        if (survey === 'lsst'   && !cfg.bands.lsst.includes(bn))   continue;
        if (survey === 'ztf dr' && !cfg.bands.ztf_dr.includes(bn)) continue;

        const v = detectionPoint(det, cfg);
        if (!v || !validPoint(v.y, survey, cfg)) continue;

        const x       = cfg.fold ? phase(det.mjd, cfg.period) : det.mjd;
        const capped  = Math.min(v.err, maxErr);
        const measId  = det.measurement_id ?? null;
        const objId   = det.objectid       ?? null;
        const field   = det.field          ?? null;

        const ptArr  = [x, v.y, measId, objId, field, capped, v.sign ?? '+'];
        const errArr = [x, v.y - capped, v.y + capped];

        pts.push(   { survey: det.survey_id, band: bn, pt: ptArr  });
        errPts.push({ survey: det.survey_id, band: bn, pt: errArr });

        if (cfg.fold) {
            pts.push(   { survey: det.survey_id, band: bn, pt: [x + 1, ...ptArr.slice(1)]  });
            errPts.push({ survey: det.survey_id, band: bn, pt: [x + 1, errArr[1], errArr[2]] });
        }
    }

    return groupedToSeries('det', groupByBand(pts), groupByBand(errPts));
}

function buildNonDetectionSeries(cfg) {
    if (!(cfg.data_types ?? ['non_detections']).includes('non_detections')) return [];
    // Non-detections are only shown in difference mode (not total) and not when folded.
    if (cfg.total || cfg.fold) return [];

    const pts = [];
    for (const nd of rawNonDetections) {
        const survey = nd.survey_id.toLowerCase();
        const bn     = bandName(nd);

        if (survey === 'ztf'    && !cfg.bands.ztf.includes(bn))    continue;
        if (survey === 'ztf dr' && !cfg.bands.ztf_dr.includes(bn)) continue;

        const y = nd.diffmaglim;
        if (!validPoint(y, survey, cfg)) continue;

        pts.push({ survey: nd.survey_id, band: bn, pt: [nd.mjd, y, null, null, null, 0, '+'] });
    }

    const out = [];
    for (const [surv, bands] of Object.entries(groupByBand(pts))) {
        for (const [band, data] of Object.entries(bands)) {
            out.push(makeSeries('lim. mag', surv, band, data));
        }
    }
    return out;
}

function buildForcedPhotSeries(cfg) {
    if (!(cfg.data_types ?? ['forced_photometry']).includes('forced_photometry')) return [];
    const maxErr = cfg.flux ? 99_999 : 1;
    const pts = [], errPts = [];

    for (const fp of rawForcedPhotometry) {
        const survey = fp.survey_id.toLowerCase();
        const bn     = bandName(fp);

        if (survey === 'lsst'   && !cfg.bands.lsst.includes(bn))   continue;
        if (survey === 'ztf'    && !cfg.bands.ztf.includes(bn))     continue;
        if (survey === 'ztf dr' && !cfg.bands.ztf_dr.includes(bn)) continue;

        const v = forcedPhotPoint(fp, cfg);
        if (!v || !validPoint(v.y, survey, cfg)) continue;

        const x      = cfg.fold ? phase(fp.mjd, cfg.period) : fp.mjd;
        const capped = Math.min(v.err, maxErr);
        const measId = fp.measurement_id ?? null;

        const ptArr  = [x, v.y, measId, null, fp.field ?? null, capped, '+'];
        const errArr = [x, v.y - capped, v.y + capped];

        pts.push(   { survey: fp.survey_id, band: bn, pt: ptArr  });
        errPts.push({ survey: fp.survey_id, band: bn, pt: errArr });

        if (cfg.fold) {
            pts.push(   { survey: fp.survey_id, band: bn, pt: [x + 1, ...ptArr.slice(1)]  });
            errPts.push({ survey: fp.survey_id, band: bn, pt: [x + 1, errArr[1], errArr[2]] });
        }
    }

    return groupedToSeries('f. phot', groupByBand(pts), groupByBand(errPts));
}

// Invisible series that forces the Y-axis to include error-bar extremes.
function buildLimitSeries(series) {
    const limits = [];
    for (const s of series) {
        if (s.error_bar && s.min_plot_error) limits.push(s.min_plot_error);
        if (s.error_bar && s.max_plot_error) limits.push(s.max_plot_error);
    }
    if (!limits.length) return [];
    return [{
        name: '', type: 'scatter', data: limits,
        color: '#00CBFF', symbol: 'none', symbolSize: 0,
        survey: 'empty', band: 'empty',
    }];
}

// ─── Band offset ──────────────────────────────────────────────────────────────
function computeMetric(name, values) {
    if (!values.length) return 99_999;
    const s = [...values].sort((a, b) => a - b);
    const n = s.length;
    if (name === 'min')    return s[0];
    if (name === 'max')    return s[n - 1];
    if (name === 'avg')    return values.reduce((a, b) => a + b, 0) / n;
    if (name === 'median') return n % 2 ? s[Math.floor(n / 2)] : (s[n / 2 - 1] + s[n / 2]) / 2;
    return 99_999;
}

function applyOffsetBands(series, cfg) {
    if (!cfg.offset_bands) return series;

    const normal   = series.filter(s => !s.error_bar);
    const errBars  = Object.fromEntries(series.filter(s => s.error_bar).map(s => [s.name, s]));
    const groups   = {};

    for (const s of normal) {
        const key = `${s.survey}::${s.band}`;
        const g   = (groups[key] ??= { series: [], metric: 0 });
        g.series.push(s);
        g.metric = computeMetric(cfg.offset_metric, g.series.flatMap(x => x.data.map(d => d[1])));
    }

    const sorted  = Object.values(groups).sort((a, b) => a.metric - b.metric);
    const out     = [];

    sorted.forEach((group, i) => {
        const offset = i * cfg.offset_num;
        for (const s of group.series) {
            const newName = offset > 0 ? `${s.name} (+${offset})` : s.name;
            out.push({ ...s, name: newName, data: s.data.map(p => [p[0], p[1] + offset, ...p.slice(2)]) });

            const eb = errBars[s.name];
            if (eb) {
                out.push({
                    ...eb, name: newName,
                    data: eb.data.map(p => [p[0], p[1] + offset]),
                    markLine: {
                        ...eb.markLine,
                        data: eb.markLine.data.map(pair => [
                            { coord: [pair[0].coord[0], pair[0].coord[1] + offset], symbol: 'none' },
                            { coord: [pair[1].coord[0], pair[1].coord[1] + offset], symbol: 'none' },
                        ]),
                    },
                });
            }
        }
    });

    return out;
}

// ─── Legend ───────────────────────────────────────────────────────────────────
function buildLegend(cfg) {
    return {
        left: 'right', top: 'middle', height: '80%', orient: 'vertical',
        selectedMode: false, itemWidth: 20,
        data: cfg.offset_bands ? null : [
            { name: 'det ZTF: g' },      { name: 'det ZTF: r' },      { name: 'det ZTF: i' },
            { name: 'lim. mag ZTF: g' }, { name: 'lim. mag ZTF: r' }, { name: 'lim. mag ZTF: i' },
            { name: 'f. phot ZTF: g' },  { name: 'f. phot ZTF: r' },  { name: 'f. phot ZTF: i' },
            { name: 'det LSST: u' },     { name: 'det LSST: g' },     { name: 'det LSST: r' },
            { name: 'det LSST: i' },     { name: 'det LSST: z' },     { name: 'det LSST: y' },
            { name: 'f. phot LSST: u' }, { name: 'f. phot LSST: g' }, { name: 'f. phot LSST: r' },
            { name: 'f. phot LSST: i' }, { name: 'f. phot LSST: z' }, { name: 'f. phot LSST: y' },
            { name: 'det ZTF DR: g' },   { name: 'det ZTF DR: r' },   { name: 'det ZTF DR: i' },
        ],
    };
}

// ─── Tooltip ──────────────────────────────────────────────────────────────────
function buildTooltip() {
    return {
        trigger: 'item',
        formatter(params) {
            const { seriesName, value } = params;
            if (!value || value.length < 7) return '';

            const isOffset = seriesName.includes('(+');
            const slide    = seriesName.includes('+') || seriesName.includes('*') ? -5 : -1;
            const band     = seriesName.includes('DR')
                ? seriesName.slice(slide) + ' DR'
                : seriesName.slice(slide);

            const plotValue = Number(value[1]).toFixed(3);
            const plotError = Number(value[5]).toFixed(3);
            const sign      = value[6] === '-' ? '(-)' : '(+)';
            const mjd       = value[0];

            let dateStr = '';
            try { dateStr = jdToDate(mjd).toUTCString().slice(0, -3) + 'UTC'; } catch (_) {}

            const table = document.createElement('div');
            table.style.cssText = 'min-width:340px;padding:0 16px';

            const rows = [
                value[2] != null ? ['Measurement id', value[2]] : null,
                value[3] != null ? ['objectid',        value[3]] : null,
                value[4] != null ? ['field',            value[4]] : null,
                [band, `${sign} ${plotValue} ± ${plotError}`],
                ['MJD',  mjd],
                ['Date', dateStr],
            ].filter(Boolean);

            for (const [label, val] of rows) {
                const row = document.createElement('div');
                row.style.cssText = 'display:flex;flex-direction:row;justify-content:flex-start;gap:16px;font-size:13px;width:100%;margin:8px 0';
                const lEl = document.createElement('div');
                lEl.style.width = '40%';
                lEl.textContent = `${label} : `;
                const vEl = document.createElement('div');
                vEl.style.cssText = 'width:60%;font-weight:bold';
                vEl.textContent = String(val);
                row.appendChild(lEl);
                row.appendChild(vEl);
                table.appendChild(row);
            }
            return table;
        },
    };
}

// ─── Full ECharts options ─────────────────────────────────────────────────────
function buildOptions(cfg) {
    const raw = [
        ...buildDetectionSeries(cfg),
        ...buildNonDetectionSeries(cfg),
        ...buildForcedPhotSeries(cfg),
    ];
    const offset  = applyOffsetBands(raw, cfg);
    const limits  = buildLimitSeries(offset.length ? offset : raw);
    const series  = [...offset, ...limits];

    return {
        title:  { show: true, text: cfg.oid },
        tooltip: {},
        grid:   { left: 'left', top: '10%', width: '75%', height: '100%' },
        legend: buildLegend(cfg),
        xAxis:  { type: 'value', name: cfg.fold ? 'Phase' : 'MJD', scale: true, splitLine: false },
        yAxis:  {
            type: 'value', name: cfg.flux ? 'Flux [nJy]' : 'Magnitude',
            scale: true, inverse: !cfg.flux,
            nameLocation: cfg.flux ? 'end' : 'start',
            splitLine: false,
        },
        series,
        animation: false,
        toolbox: {
            show: true, orient: 'horizontal',
            feature: { dataZoom: { show: true }, dataView: { show: false }, saveAsImage: { show: true } },
        },
    };
}

// ─── Periodogram options ──────────────────────────────────────────────────────
function buildPeriodogramOptions() {
    const p           = rawPeriodogram;
    const bestSet     = new Set(p.best_periods_index ?? []);
    const regular     = [];
    const best        = [];

    for (let i = 0; i < (p.periods ?? []).length; i++) {
        (bestSet.has(i) ? best : regular).push([p.periods[i], p.scores[i]]);
    }

    const opts = {
        tooltip:  { axisPointer: { type: 'cross' }, formatter: params => `<b>Period:</b> ${params.data[0]} <b>Score:</b> ${params.data[1]}` },
        grid:     { left: 'left', top: '10%', width: '75%', height: '100%' },
        legend:   { left: 'right', top: 'middle', height: '80%', orient: 'vertical' },
        xAxis:    { type: 'log', name: 'Period', scale: true, splitLine: false, min: '0.05', max: '500' },
        yAxis:    { type: 'value', name: 'Score', scale: true, splitLine: false },
        series:   [
            { name: 'periods',      type: 'scatter', data: regular },
            { name: 'best periods', type: 'scatter', data: best, symbol: 'triangle', color: 'red' },
        ],
        animation: false,
    };
    return opts;
}

// ─── Corrected detection check ────────────────────────────────────────────────
function isNotCorrected() {
    if (!rawDetections.length) return true;
    const d = rawDetections[0];
    const s = d.survey_id?.toLowerCase();
    if (s === 'ztf')  return (d.magpsf_corr ?? 0) === 0;
    if (s === 'lsst') return (d.scienceFlux  ?? 0) === 0;
    return false;
}

// ─── Chart instances ──────────────────────────────────────────────────────────
let myChart = null;
let pChart  = null;

function initChart() {
    const dom = document.getElementById('chart');
    if (!dom) return;
    myChart?.dispose();
    myChart = echarts.init(dom, currentTheme());

    const opts = buildOptions(config);
    opts.tooltip = buildTooltip();
    myChart.setOption(opts);

    const grid = document.getElementById('plot-grid');
    if (grid) new ResizeObserver(() => myChart?.resize()).observe(grid);

    document.getElementById('toggle-theme-lc')?.addEventListener('click', () => {
        myChart?.dispose();
        myChart = echarts.init(dom, currentTheme());
        const o = buildOptions(config);
        o.tooltip = buildTooltip();
        myChart.setOption(o);
        reinitPeriodogram();
    });
}

function initPeriodogram() {
    const dom = document.getElementById('periodogram');
    if (!dom || !(rawPeriodogram?.periods?.length)) return;
    pChart?.dispose();
    pChart = echarts.init(dom, currentTheme());
    pChart.setOption(buildPeriodogramOptions());

    pChart.on('click', params => {
        dom.dispatchEvent(new CustomEvent('periodogram:periodSelected', {
            detail: { period: params.data[0].toFixed(7) },
            bubbles: true,
        }));
    });
    window.addEventListener('resize', () => pChart?.resize());
}

function reinitPeriodogram() {
    const dom = document.getElementById('periodogram');
    if (!dom) return;
    pChart?.dispose();
    pChart = echarts.init(dom, currentTheme());
    pChart.setOption(buildPeriodogramOptions());
}

function updateChart() {
    if (!myChart) return;
    const opts = buildOptions(config);
    opts.tooltip = buildTooltip();
    myChart.setOption(opts, true);
}

// ─── Visibility management ────────────────────────────────────────────────────
// True while the /htmx/periodogram fetch is in-flight.
let periodogramLoading = false;

function updateVisibility() {
    const warning        = document.getElementById('not-corrected-warning');
    const plotGrid       = document.getElementById('plot-grid');
    const pdContainer    = document.getElementById('periodogram-container');
    const noperiodMsg    = document.getElementById('no-period-message');
    const loadingMsg     = document.getElementById('periodogram-loading');

    const showWarning  = config.total && isNotCorrected();
    warning?.classList.toggle('tw-hidden', !showWarning);
    plotGrid?.classList.toggle('tw-hidden', showWarning);

    const hasPeriod    = (rawPeriodogram?.best_periods_index?.length ?? 0) > 0;
    const showPd       = config.fold && config.periodogram_enabled;

    // Enable/disable the periodogram toggle based on fold state.
    const pdToggleEl = document.querySelector('[name="periodogram_enabled"]');
    if (pdToggleEl) pdToggleEl.disabled = !config.fold;

    if (pdContainer) {
        pdContainer.classList.toggle('tw-hidden', !showPd);
        if (showPd) {
            // Loading spinner has priority over the chart or the "no period" message.
            loadingMsg?.classList.toggle('tw-hidden', !periodogramLoading);
            document.getElementById('periodogram')?.classList.toggle('tw-hidden', !hasPeriod || periodogramLoading);
            noperiodMsg?.classList.toggle('tw-hidden', hasPeriod || periodogramLoading);
            if (hasPeriod && !pChart) initPeriodogram();
            else if (hasPeriod && pChart) pChart.resize();
        }
    }

    // Show/hide ZTF DR band-toggle row based on external sources enabled.
    document.querySelector('.ztf-dr-bands-row')?.classList.toggle(
        'tw-hidden', !(config.external_sources?.enabled)
    );
}

// ─── Read config from form ────────────────────────────────────────────────────
function readConfigFromForm() {
    const form = document.getElementById('config-form');
    if (!form) return;

    const bool = name => form.querySelector(`[name="${name}"]`)?.checked ?? false;

    config.flux               = bool('flux');
    config.total              = bool('total');
    config.fold               = bool('fold');
    config.offset_bands       = bool('offset_bands');
    config.periodogram_enabled = bool('periodogram_enabled');
    config.external_sources   ??= {};
    config.external_sources.enabled = bool('external_sources.enabled');

    const period = parseFloat(form.querySelector('[name="period"]')?.value);
    if (!isNaN(period)) config.period = period;

    const offsetNum = parseInt(form.querySelector('[name="offset_num"]')?.value);
    if (!isNaN(offsetNum)) config.offset_num = offsetNum;

    const offsetMetric = form.querySelector('[name="offset_metric"]')?.value;
    if (offsetMetric) config.offset_metric = offsetMetric;

    config.bands.ztf    = [...form.querySelectorAll('[name="bands.ztf[]"]:checked')]   .map(el => el.value);
    config.bands.lsst   = [...form.querySelectorAll('[name="bands.lsst[]"]:checked')]  .map(el => el.value);
    config.bands.ztf_dr = [...form.querySelectorAll('[name="bands.ztf_dr[]"]:checked')].map(el => el.value);
    config.data_types   = [...form.querySelectorAll('[name="data_types[]"]:checked')]  .map(el => el.value);

    // Validate: fold/external sources force total mode.
    if (config.fold || config.external_sources.enabled) {
        config.total = true;
        const totalEl = form.querySelector('[name="total"]');
        if (totalEl) totalEl.checked = true;
    }
}

// ─── External sources: load ZTF DR detections via fetch ──────────────────────
/**
 * Called by the "Ok" button in the external-sources picker dialog.
 * Fetches ZTF DR detections from the server and adds them to the local pool.
 */
window.lcApplyDrSources = async function (form) {
    const selected = [...form.querySelectorAll('[name="external_sources.selected_objects[]"]:checked')]
        .map(el => el.value);

    try {
        const apiUrl = window.__LC_DATA__.apiUrl;
        const ra     = config.meanra;
        const dec    = config.meandec;
        const url    = `${apiUrl}/htmx/dr_detections?ra=${ra}&dec=${dec}&oids=${selected.join(',')}`;
        const resp   = await fetch(url);
        if (!resp.ok) throw new Error(`DR fetch failed: ${resp.status}`);
        drDetections = await resp.json();
    } catch (e) {
        console.error('Failed to load ZTF DR detections:', e);
        drDetections = [];
    }

    // Dismiss the picker overlay.
    document.getElementById('dr-picker-container')?.classList.add('tw-hidden');

    updateChart();
};

// ─── Lazy periodogram loader ──────────────────────────────────────────────────
async function loadPeriodogram() {
    if (rawPeriodogram?.periods?.length || periodogramLoading) return;
    periodogramLoading = true;
    updateVisibility();
    try {
        const apiUrl = window.__LC_DATA__.apiUrl;
        const r = await fetch(`${apiUrl}/htmx/periodogram?oid=${config.oid}&survey_id=${config.survey_id}`);
        if (!r.ok) throw new Error(r.status);
        rawPeriodogram = await r.json();
        // Adopt best period into the controls if the user hasn't changed it yet.
        if (config.period === 0.05 && rawPeriodogram.best_periods_index?.length) {
            const bestIdx = rawPeriodogram.best_periods_index[0];
            config.period = parseFloat(rawPeriodogram.periods[bestIdx].toFixed(7));
            const periodEl = document.querySelector('[name="period"]');
            const sliderEl = document.getElementById('period-slider');
            if (periodEl) periodEl.value = config.period;
            if (sliderEl) sliderEl.value  = config.period;
        }
    } catch (e) {
        console.error('Periodogram load failed:', e);
    } finally {
        periodogramLoading = false;
        updateVisibility();
        updateChart();
    }
}

// ─── Init ─────────────────────────────────────────────────────────────────────
function init() {
    initChart();
    updateVisibility();

    const form = document.getElementById('config-form');
    if (!form) return;

    // Debounce continuous inputs (sliders) slightly to avoid rebuilding on every tick.
    let debounceTimer = null;
    let prevExtEnabled       = config.external_sources?.enabled ?? false;
    let prevPeriodogramEnabled = config.periodogram_enabled;

    function onFormChange() {
        readConfigFromForm();
        updateVisibility();
        updateChart();

        // Lazy-load periodogram the first time the periodogram toggle is switched on.
        const pdNow = config.periodogram_enabled;
        if (pdNow && !prevPeriodogramEnabled) loadPeriodogram();
        prevPeriodogramEnabled = pdNow;

        const extNow = config.external_sources?.enabled ?? false;
        if (extNow && !prevExtEnabled) {
            // Auto-load all DR detections immediately (no picker required).
            const apiUrl = window.__LC_DATA__.apiUrl;
            fetch(`${apiUrl}/htmx/dr_detections?ra=${config.meanra}&dec=${config.meandec}&oids=`)
                .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
                .then(data => { drDetections = data; updateChart(); })
                .catch(e => console.error('DR auto-load failed:', e));
        } else if (!extNow && prevExtEnabled) {
            drDetections = [];
        }
        prevExtEnabled = extNow;
    }
    function onFormInput(e) {
        if (e.target.name === 'period' || e.target.id === 'period-slider' || e.target.name === 'offset_num') {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => { readConfigFromForm(); updateChart(); }, 80);
        }
    }

    form.addEventListener('change', onFormChange);
    form.addEventListener('input',  onFormInput);

    // Period selection from periodogram click.
    document.addEventListener('periodogram:periodSelected', e => {
        config.period = parseFloat(e.detail.period);
        const periodEl = document.querySelector('[name="period"]');
        const sliderEl = document.getElementById('period-slider');
        if (periodEl) periodEl.value = config.period;
        if (sliderEl) sliderEl.value  = config.period;
        updateChart();
    });
}

init();

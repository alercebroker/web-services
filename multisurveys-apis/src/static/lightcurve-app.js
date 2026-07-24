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
// All per-object state lives in these module-level bindings. loadState() (re)reads
// them from window.__LC_DATA__ so the widget can be re-initialised in place when the
// parent app swaps in a new object via HTMX — see boot() at the bottom of this file.
let rawDetections, rawNonDetections, rawForcedPhotometry;
// Periodogram data – populated lazily the first time the user enables fold mode.
let rawPeriodogram;
// Mutable config driven by the config panel controls.
let config;
// True while the /htmx/periodogram fetch is in-flight.
let periodogramLoading = false;
// True once the user has manually changed the period (slider / input / X2 / /2 /
// periodogram click). Once set, we stop overriding the period with the periodogram's
// best candidate.
let periodUserModified = false;
// Guard so programmatic period updates (applyBestCandidatePeriod) don't trip the
// user-modified flag via the form's input/change handlers.
let settingPeriodProgrammatically = false;
// ZTF Data-Release detections loaded on demand (external sources feature).
let drDetections = [];

// Load (or reload) all per-object state from the data the layout template embedded.
// Called by boot() on first load and again on every HTMX swap of a new object.
function loadState() {
    const data = window.__LC_DATA__;
    rawDetections       = data.detections;
    rawNonDetections    = data.nonDetections;
    rawForcedPhotometry = data.forcedPhotometry;
    rawPeriodogram      = data.periodogram;
    config              = JSON.parse(JSON.stringify(data.config));
    // Reset interaction flags so a freshly-loaded object starts clean.
    periodogramLoading            = false;
    periodUserModified            = false;
    settingPeriodProgrammatically = false;
    drDetections                  = [];
}

// Bound to `document` exactly once per page (see init()); survives re-inits.
let documentListenersBound = false;

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
function phase(mjd, period) {
    return (mjd % period) / period;
}

function isDark() {
    return document.getElementById('main-app')?.classList.contains('tw-dark') ?? false;
}

function currentTheme() {
    return isDark() ? customDarkTheme : 'light';
}

// ─── Photometry variant lookup ────────────────────────────────────────────────
// The flux<->magnitude conversion lives entirely in the Python models
// (see plot_variants() in models/, surfaced by *_plot_record in service.py). The
// server precomputes all four flux/total combinations per point, so here we only
// *select* the one matching the current toggles — no zero points or error
// propagation are reimplemented in JS, and nothing can drift out of sync.
function variantKey(cfg) {
    return `${cfg.flux ? 'flux' : 'mag'}_${cfg.total ? 'total' : 'diff'}`;
}

/**
 * Returns the precomputed { y, err, sign } for a detection or forced-photometry
 * point under the current config, or null if the point has no variants.
 */
function pointValue(item, cfg) {
    return item.variants?.[variantKey(cfg)] ?? null;
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
        const bn     = det.band;

        if (survey === 'ztf'    && !cfg.bands.ztf.includes(bn))    continue;
        if (survey === 'lsst'   && !cfg.bands.lsst.includes(bn))   continue;
        if (survey === 'ztf dr' && !cfg.bands.ztf_dr.includes(bn)) continue;

        const v = pointValue(det, cfg);
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
        const bn     = nd.band;

        if (survey === 'ztf'    && !cfg.bands.ztf.includes(bn))    continue;
        if (survey === 'ztf dr' && !cfg.bands.ztf_dr.includes(bn)) continue;

        const y = nd.mag;
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
        const bn     = fp.band;

        if (survey === 'lsst'   && !cfg.bands.lsst.includes(bn))   continue;
        if (survey === 'ztf'    && !cfg.bands.ztf.includes(bn))     continue;
        if (survey === 'ztf dr' && !cfg.bands.ztf_dr.includes(bn)) continue;

        const v = pointValue(fp, cfg);
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
// Computed server-side (see the /lightcurve route) using the same model conversion
// the plot relies on, so the browser doesn't reimplement the "is it corrected" rule.
function isNotCorrected() {
    return window.__LC_DATA__.notCorrected ?? false;
}

// ─── Chart instances ──────────────────────────────────────────────────────────
let myChart = null;
let pChart  = null;
// The periodogram's window-resize listener is bound once per page. initPeriodogram()
// can now run many times (every render), so guard it to avoid stacking listeners.
let pdResizeBound = false;

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
        // Rebuild the scatter so it picks up the new theme (and re-binds its click
        // handler — the single builder below guarantees the handler survives).
        initPeriodogram();
    });
}

// Canonical periodogram builder. Safe to call repeatedly: every call disposes any
// existing instance and re-applies the current rawPeriodogram, so the scatter always
// reflects the freshly loaded data (and never keeps stale points or loses its click
// handler). Requires the container to be visible so ECharts can size it.
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
    if (!pdResizeBound) {
        pdResizeBound = true;
        window.addEventListener('resize', () => pChart?.resize());
    }
}

function updateChart() {
    if (!myChart) return;
    // When fold is requested but the periodogram (and thus the period) isn't ready
    // yet, don't render a fold at a meaningless period — leave the current chart in
    // place and let updateVisibility() show the "Computing period…" spinner. Once the
    // periodogram arrives, loadPeriodogram() calls updateChart() again and we render.
    const foldPending = config.fold && !(rawPeriodogram?.periods?.length);
    if (foldPending) return;

    const opts = buildOptions(config);
    opts.tooltip = buildTooltip();
    myChart.setOption(opts, true);
}

// ─── Visibility management ────────────────────────────────────────────────────
function updateVisibility() {
    const warning        = document.getElementById('not-corrected-warning');
    const plotGrid       = document.getElementById('plot-grid');
    const pdContainer    = document.getElementById('periodogram-container');
    const noperiodMsg    = document.getElementById('no-period-message');
    const loadingMsg     = document.getElementById('periodogram-loading');
    const foldLoading    = document.getElementById('fold-loading');

    const showWarning  = config.total && isNotCorrected();
    warning?.classList.toggle('tw-hidden', !showWarning);
    plotGrid?.classList.toggle('tw-hidden', showWarning);

    const hasPeriods   = (rawPeriodogram?.periods?.length ?? 0) > 0;
    const showPd       = config.fold && config.periodogram_enabled;

    // Plot-area spinner while we wait for the period to fold the lightcurve.
    const showFoldSpinner = config.fold && periodogramLoading && !hasPeriods;
    foldLoading?.classList.toggle('tw-hidden', !showFoldSpinner);

    // Enable/disable the periodogram toggle based on fold state.
    const pdToggleEl = document.querySelector('[name="periodogram_enabled"]');
    if (pdToggleEl) pdToggleEl.disabled = !config.fold;

    if (pdContainer) {
        pdContainer.classList.toggle('tw-hidden', !showPd);
        if (showPd) {
            // The periodogram chart shows whenever there are periods to plot (even for
            // non-periodic objects). The "no data" message only appears once a load has
            // completed and there are genuinely no periods.
            const emptyAfterLoad = !periodogramLoading && hasPeriods === false && rawPeriodogram?.periods != null;
            // Loading spinner has priority over the chart or the "no data" message.
            loadingMsg?.classList.toggle('tw-hidden', !periodogramLoading);
            document.getElementById('periodogram')?.classList.toggle('tw-hidden', !hasPeriods || periodogramLoading);
            noperiodMsg?.classList.toggle('tw-hidden', !emptyAfterLoad || periodogramLoading);
            // Always rebuild against the current data whenever the scatter is shown,
            // rather than resizing a possibly-stale instance. initPeriodogram() is a
            // no-op flicker-wise (animation is off) and keeps the plot in sync.
            if (hasPeriods) initPeriodogram();
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

// ─── Best-candidate period adoption ───────────────────────────────────────────
// When fold is on and the user hasn't manually set a period, adopt the periodogram's
// best candidate (formal best, or top-scoring candidate for non-periodic objects).
// Updates the form controls programmatically without tripping periodUserModified.
function applyBestCandidatePeriod() {
    if (rawPeriodogram?.best_candidate_period == null) return;
    if (!config.fold || periodUserModified) return;

    config.period = rawPeriodogram.best_candidate_period;
    settingPeriodProgrammatically = true;
    try {
        const periodEl = document.querySelector('[name="period"]');
        const sliderEl = document.getElementById('period-slider');
        if (periodEl) periodEl.value = config.period;
        if (sliderEl) sliderEl.value  = config.period;
    } finally {
        settingPeriodProgrammatically = false;
    }
}

// ─── Lazy periodogram loader ──────────────────────────────────────────────────
async function loadPeriodogram() {
    // One-shot: don't refetch if we already have the data or a fetch is in flight.
    if (rawPeriodogram?.periods?.length || periodogramLoading) return;
    periodogramLoading = true;
    updateVisibility();
    try {
        const apiUrl = window.__LC_DATA__.apiUrl;
        const r = await fetch(`${apiUrl}/htmx/periodogram?oid=${config.oid}&survey_id=${config.survey_id}`);
        if (!r.ok) throw new Error(r.status);
        rawPeriodogram = await r.json();
        applyBestCandidatePeriod();
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
    let prevFold             = config.fold;

    function onFormChange(e) {
        // The period input fires a bubbling `change` for direct edits and for the
        // X2 / /2 buttons (which dispatch change on the input). Treat those as manual
        // period changes — unless we set the value programmatically.
        if (e && (e.target?.name === 'period' || e.target?.id === 'period-slider') && !settingPeriodProgrammatically) {
            periodUserModified = true;
        }

        readConfigFromForm();

        // Fold path: fetch the periodogram exactly once, only on the OFF→ON
        // transition of the Fold toggle. Toggling fold back off and on won't refetch
        // (loadPeriodogram is one-shot guarded anyway), and other form changes while
        // fold stays on never trigger the endpoint.
        const foldNow = config.fold;
        if (foldNow && !prevFold) {
            if (!(rawPeriodogram?.periods?.length)) {
                // Not ready yet — kick off the (guarded) load. The spinner shows via
                // updateVisibility/updateChart; updateChart re-runs when data arrives.
                loadPeriodogram();
            } else {
                // Already have data — fold immediately at the best candidate.
                applyBestCandidatePeriod();
            }
        }
        prevFold = foldNow;

        updateVisibility();
        updateChart();

        // The periodogram chart still needs data when its toggle turns on. The
        // loadPeriodogram() guard makes this harmless if fold already triggered it.
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
            // A user-driven period change pins the period — stop auto-adopting the
            // periodogram candidate. Programmatic updates set a guard so they don't.
            if ((e.target.name === 'period' || e.target.id === 'period-slider') && !settingPeriodProgrammatically) {
                periodUserModified = true;
            }
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => { readConfigFromForm(); updateChart(); }, 80);
        }
    }

    // This form is purely client-side (no action/method). Pressing Enter in a text
    // field (e.g. the period box) would otherwise trigger the browser's implicit
    // submit — a GET navigation to the current URL without oid/survey_id, which 422s
    // and tears down the widget. Block it; the period change already applied via `change`.
    form.addEventListener('submit', e => e.preventDefault());

    form.addEventListener('change', onFormChange);
    form.addEventListener('input',  onFormInput);

    // Period selection from periodogram click — counts as a manual change.
    // Bound on `document` once per page: init() runs again on every HTMX swap, but
    // this listener (unlike the form listeners above, whose elements are replaced by
    // the swap) would otherwise stack up an extra copy per object change.
    if (!documentListenersBound) {
        documentListenersBound = true;
        document.addEventListener('periodogram:periodSelected', e => {
            config.period = parseFloat(e.detail.period);
            periodUserModified = true;
            settingPeriodProgrammatically = true;
            try {
                const periodEl = document.querySelector('[name="period"]');
                const sliderEl = document.getElementById('period-slider');
                if (periodEl) periodEl.value = config.period;
                if (sliderEl) sliderEl.value  = config.period;
            } finally {
                settingPeriodProgrammatically = false;
            }
            updateChart();
        });
    }
}

// ─── Boot ─────────────────────────────────────────────────────────────────────
// (Re)initialise the whole widget from the current window.__LC_DATA__. Exposed
// globally so the layout's inline script can re-run it after an HTMX swap brings in
// a new object — the browser evaluates this ES module only once per page load, so
// without this hook a swapped-in object would never get its chart initialised.
function boot() {
    // An HTMX swap replaces the chart DOM nodes, so any existing ECharts instances are
    // bound to detached nodes. Dispose and clear them both so init() (for the main
    // chart) and updateVisibility() (for the lazily-built periodogram) rebuild against
    // the fresh DOM. Without this the periodogram's `!pChart` guard would keep resizing
    // the stale instance and never render on the new node.
    myChart?.dispose(); myChart = null;
    pChart?.dispose();  pChart  = null;
    loadState();
    init();
}
window.__lcBoot = boot;
boot();

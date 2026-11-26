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
// Outcome of the last periodogram fetch that brought no periods: 'empty' or 'failed'.
let periodogramStatus = null;
// True once the user has manually changed the period (input / step buttons / X2 / /2 /
// periodogram click). Once set, we stop overriding the period with the periodogram's
// best candidate.
let periodUserModified = false;
// Guard so programmatic period updates (applyBestCandidatePeriod) don't trip the
// user-modified flag via the form's input/change handlers.
let settingPeriodProgrammatically = false;
// ZTF Data-Release detections loaded on demand (external sources feature).
let drDetections = [];
// Object group (association): the members and nearby objects listed in the config panel, or null.
let groupInfo = null;
// Photometry of other objects of the group, fetched on demand: key "survey:oid" → { detections, forcedPhotometry }.
let groupPhot = new Map();
// Keys being fetched right now, so a second change doesn't fetch them twice.
let groupLoading = new Set();
// Other objects the current periodogram was searched on, besides the viewed one: their sorted keys, comma-joined
// ('' for none). Compared with the objects drawn now to offer "Recompute" (updatePeriodSource).
let periodogramObjects = '';

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
    periodogramStatus             = null;
    periodUserModified            = false;
    settingPeriodProgrammatically = false;
    drDetections                  = [];
    groupInfo                     = data.group ?? null;
    groupPhot                     = new Map();
    groupLoading                  = new Set();
    periodogramObjects            = '';
    // Nothing of the group is drawn until the user turns on "Show on the light curve".
    config.group_selected         = [];
}

// Bound to `document` exactly once per page (see init()); survives re-inits.
let documentListenersBound = false;

// ─── Visual constants ─────────────────────────────────────────────────────────
// Color says the band and the marker says the survey (SYMBOLS), as in the experimental explorer: g is
// the same green in ZTF and LSST, so the two surveys of a band read as one curve.
const BAND_COLORS = { u: '#56B4E9', g: '#009E73', r: '#D55E00', i: '#E69F00', z: '#CC79A7', y: '#0072B2' };
const COLORS = {
    'ztf':    BAND_COLORS,
    'lsst':   BAND_COLORS,
    'ztf dr': BAND_COLORS,
    'empty':  { empty: '#00CBFF' },
};

// Same font as the Explorer and the side panel (static/lightcurve-panel.css)
const CHART_FONT = 'Roboto, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif';

const NDL_SYMBOL =
    'path://M0,49.017c0-13.824,11.207-25.03,25.03-25.03h438.017c13.824,0,25.029,' +
    '11.207,25.029,25.03L262.81,455.745c0,0-18.772,18.773-37.545,0C206.494,436.973,0,49.017,0,49.017z';

// Detections are filled: squares for ZTF, circles for LSST. Forced photometry is a hollow triangle, pointing
// down for ZTF and up for LSST (SYMBOL_ROTATE). ZTF DR points are small faint hollow squares.
const SYMBOLS = {
    'ztf':    { det: 'rect',   'lim. mag': NDL_SYMBOL, 'f. phot': 'triangle' },
    'lsst':   { det: 'circle',                         'f. phot': 'triangle' },
    'ztf dr': { det: 'rect',   'lim. mag': NDL_SYMBOL, 'f. phot': 'triangle' },
    'empty':  { empty: 'none' },
};
const SYMBOL_ROTATE = { 'ztf': { 'f. phot': 180 }, 'ztf dr': { 'f. phot': 180 } };
const HOLLOW = new Set(['f. phot']);

// Other objects of the group are drawn darker and translucent, so the object being viewed stands out.
const MEMBER_DARKEN  = 0.7;
const MEMBER_OPACITY = 0.5;

function darken(hex, factor) {
    const rgb = [1, 3, 5].map(i => Math.round(parseInt(hex.slice(i, i + 2), 16) * factor));
    return '#' + rgb.map(v => v.toString(16).padStart(2, '0')).join('');
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
function phase(mjd, period) {
    return (mjd % period) / period;
}

// ─── Fold times ───────────────────────────────────────────────────────────────
// The server sends each point's BJD_TDB (`bjd_tdb`): the time at the Solar System barycentre, on one clock and
// at mid-exposure, whatever the survey (core/periodogram/barycentric.py). Folding on the observed MJD instead
// blurs short periods by up to ±8.3 min over the year (Earth's orbit) and shifts ZTF from LSST by about 52 s;
// ZTF DR points come heliocentric already. The periodogram uses the same times. The fold uses BJD_TDB only when
// every point drawn has it, else the observed MJD for all: never a mix of the two.
function foldsOnBjd(cfg) {
    if (!cfg.fold) return false;
    const drawn = [
        ...rawDetections, ...rawForcedPhotometry,
        ...groupPoints('detections', cfg), ...groupPoints('forcedPhotometry', cfg),
        ...(cfg.external_sources?.enabled ? drDetections : []),
    ];
    return drawn.every(p => Number.isFinite(p.bjd_tdb));
}

function xValue(point, cfg) {
    return cfg.fold ? phase(cfg.fold_on_bjd ? point.bjd_tdb : point.mjd, cfg.period) : point.mjd;
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
    if (cfg.flux) {
        const lim = 99_999_999;
        return y > -lim && y < lim;
    }
    return y > 0 && y < 99;
}

// ─── ECharts series factories ─────────────────────────────────────────────────
// Points carry their observed MJD at index 8 and their BJD_TDB at index 9 (the x is the phase when folded).
const POINT_MJD = 8;
const POINT_BJD = 9;
// Points of other objects of the group carry that object's id at index 7. They go in series of their own
// (`member`), drawn darker and translucent, with the same name as the viewed object's series of that survey,
// type and band, so the band offset and the legend treat them as one.
const POINT_OBJECT = 7;

function seriesColor(sk, band, member) {
    const color = COLORS[sk]?.[band] ?? '#888888';
    return member ? darken(color, MEMBER_DARKEN) : color;
}

function makeSeries(type, survey, band, data, member = false) {
    const sk     = survey.toLowerCase();
    const color  = seriesColor(sk, band, member);
    const dr     = sk === 'ztf dr';
    const hollow = HOLLOW.has(type) || dr;
    return {
        name:       `${type} ${survey.toUpperCase()}: ${band}`,
        type:       'scatter',
        data,
        color,
        itemStyle:  {
            color:       hollow ? 'rgba(0,0,0,0)' : color,
            borderColor: color,
            borderWidth: hollow ? 1.5 : 0,
            opacity:     member ? MEMBER_OPACITY : dr ? 0.6 : 1,
        },
        symbol:       SYMBOLS[sk]?.[type]  ?? 'circle',
        symbolRotate: SYMBOL_ROTATE[sk]?.[type] ?? 0,
        symbolSize:   dr ? 6 : 8,
        survey:       sk,
        z:            dr ? 2 : member ? 5 : 10,
        band,
        member,
    };
}

function makeErrorBarSeries(type, survey, band, errData, member = false) {
    const sk    = survey.toLowerCase();
    const color = seriesColor(sk, band, member);
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
            lineStyle: { color, type: 'solid', opacity: member ? MEMBER_OPACITY : 1 },
        },
        error_bar:      true,
        min_plot_error: minPt,
        max_plot_error: maxPt,
        survey:         sk,
        band,
        member,
    };
}

// ─── Point grouping ───────────────────────────────────────────────────────────
// One group per survey, band and whether the points are of another member of the group.
function groupByBand(points) {
    const g = {};
    for (const { survey, band, pt, member = false } of points) {
        (g[`${survey}|${band}|${member}`] ??= { survey, band, member, data: [] }).data.push(pt);
    }
    return Object.values(g);
}

function groupedToSeries(type, grouped, grouped_err) {
    return [
        ...grouped.map(g => makeSeries(type, g.survey, g.band, g.data, g.member)),
        ...grouped_err.map(g => makeErrorBarSeries(type, g.survey, g.band, g.data, g.member)),
    ];
}

// ─── Series builders ──────────────────────────────────────────────────────────
// Points of the other objects of the group that are switched on and already fetched.
function groupPoints(kind, cfg) {
    const out = [];
    for (const key of cfg.group_selected ?? []) {
        const phot = groupPhot.get(key);
        if (phot) out.push(...phot[kind]);
    }
    return out;
}

function buildDetectionSeries(cfg) {
    if (!(cfg.data_types ?? ['detections']).includes('detections')) return [];
    const all     = [
        ...rawDetections,
        ...groupPoints('detections', cfg),
        ...(cfg.external_sources?.enabled ? drDetections : []),
    ];
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

        const x       = xValue(det, cfg);
        const capped  = Math.min(v.err, maxErr);
        const measId  = det.measurement_id ?? null;
        const objId   = det.objectid       ?? null;
        const field   = det.field          ?? null;

        const ptArr  = [x, v.y, measId, objId, field, capped, v.sign ?? '+', det.oid ?? null, det.mjd, det.bjd_tdb ?? null];
        const errArr = [x, v.y - capped, v.y + capped];

        const member = det.oid != null;
        pts.push(   { survey: det.survey_id, band: bn, member, pt: ptArr  });
        errPts.push({ survey: det.survey_id, band: bn, member, pt: errArr });

        if (cfg.fold) {
            pts.push(   { survey: det.survey_id, band: bn, member, pt: [x + 1, ...ptArr.slice(1)]  });
            errPts.push({ survey: det.survey_id, band: bn, member, pt: [x + 1, errArr[1], errArr[2]] });
        }
    }

    return groupedToSeries('det', groupByBand(pts), groupByBand(errPts));
}

function buildNonDetectionSeries(cfg) {
    if (!(cfg.data_types ?? ['non_detections']).includes('non_detections')) return [];
    // Non-detections are limiting magnitudes, so they are only shown in magnitude view,
    // in difference mode (not total) and not when folded.
    if (cfg.flux || cfg.total || cfg.fold) return [];

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

    // Fainter than the detections (ECharts' default 0.8), as in alerce.online, which drew
    // them in a 50% transparent band color: 0.5 × 0.8.
    return groupByBand(pts).map(g => {
        const s = makeSeries('lim. mag', g.survey, g.band, g.data);
        return { ...s, itemStyle: { ...s.itemStyle, opacity: 0.4 } };
    });
}

function buildForcedPhotSeries(cfg) {
    if (!(cfg.data_types ?? ['forced_photometry']).includes('forced_photometry')) return [];
    const maxErr = cfg.flux ? 99_999 : 1;
    const pts = [], errPts = [];

    for (const fp of [...rawForcedPhotometry, ...groupPoints('forcedPhotometry', cfg)]) {
        const survey = fp.survey_id.toLowerCase();
        const bn     = fp.band;

        if (survey === 'lsst'   && !cfg.bands.lsst.includes(bn))   continue;
        if (survey === 'ztf'    && !cfg.bands.ztf.includes(bn))     continue;
        if (survey === 'ztf dr' && !cfg.bands.ztf_dr.includes(bn)) continue;

        const v = pointValue(fp, cfg);
        if (!v || !validPoint(v.y, survey, cfg)) continue;

        const x      = xValue(fp, cfg);
        const capped = Math.min(v.err, maxErr);
        const measId = fp.measurement_id ?? null;

        const ptArr  = [x, v.y, measId, null, fp.field ?? null, capped, v.sign ?? '+', fp.oid ?? null, fp.mjd, fp.bjd_tdb ?? null];
        const errArr = [x, v.y - capped, v.y + capped];

        const member = fp.oid != null;
        pts.push(   { survey: fp.survey_id, band: bn, member, pt: ptArr  });
        errPts.push({ survey: fp.survey_id, band: bn, member, pt: errArr });

        if (cfg.fold) {
            pts.push(   { survey: fp.survey_id, band: bn, member, pt: [x + 1, ...ptArr.slice(1)]  });
            errPts.push({ survey: fp.survey_id, band: bn, member, pt: [x + 1, errArr[1], errArr[2]] });
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
    // The viewed object's series and the other members' share a name: tell their error bars apart.
    const errKey   = s => `${s.name}|${!!s.member}`;
    const errBars  = Object.fromEntries(series.filter(s => s.error_bar).map(s => [errKey(s), s]));
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

            const eb = errBars[errKey(s)];
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
// The band and type toggles of the side panel carry each series' color and marker,
// so the chart has no legend of its own. It comes back with the band offset on,
// to show how much each band was shifted ("det LSST: g (+2)").
function buildLegend(cfg) {
    return {
        show: !!cfg.offset_bands,
        left: 'right', top: 'middle', height: '80%', orient: 'vertical',
        selectedMode: false, itemWidth: 20,
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
            const mjd       = value[POINT_MJD] ?? value[0];
            const bjd       = value[POINT_BJD];

            let dateStr = '';
            try { dateStr = jdToDate(mjd).toUTCString().slice(0, -3) + 'UTC'; } catch (_) {}

            // Series are named "<type> <SURVEY>: <band>" (makeSeries). The point's object: another
            // member of the group, a ZTF DR object, or else the object being viewed.
            const [, kind, survey] = seriesName.match(/^(det|lim\. mag|f\. phot) ([^:]+):/) ?? [];
            const object = value[POINT_OBJECT] ?? value[3] ?? window.__LC_DATA__.objectName ?? config.oid;
            const KINDS = { 'det': 'Detection', 'f. phot': 'Forced photometry', 'lim. mag': 'Upper limit' };

            const box = document.createElement('div');
            box.style.cssText = 'font-size:12px;line-height:1.4';
            const head = document.createElement('div');
            head.style.cssText = 'font-weight:600;margin-bottom:3px';
            head.textContent = `${object} (${survey})`;
            box.appendChild(head);

            const rows = [
                kind ? ['Type', KINDS[kind]] : null,
                [band, `${sign} ${plotValue} ± ${plotError}`],
                ['MJD',  Number(mjd).toFixed(5)],
                ['Date', dateStr],
                config.fold ? ['Phase', Number(value[0] % 1).toFixed(4)] : null,
                config.fold && config.fold_on_bjd && bjd != null ? ['BJD_TDB', Number(bjd).toFixed(6)] : null,
                value[2] != null ? ['Measurement id', value[2]] : null,
                value[4] != null ? ['Field',          value[4]] : null,
            ].filter(Boolean);

            const grid = document.createElement('div');
            grid.style.cssText = 'display:grid;grid-template-columns:auto auto;column-gap:10px';
            for (const [label, val] of rows) {
                const lEl = document.createElement('span');
                lEl.style.opacity = '0.7';
                lEl.textContent = label;
                const vEl = document.createElement('span');
                vEl.style.fontWeight = '600';
                vEl.textContent = String(val);
                grid.append(lEl, vEl);
            }
            box.appendChild(grid);
            return box;
        },
        padding: [6, 10],
    };
}

// ─── Full ECharts options ─────────────────────────────────────────────────────
function buildOptions(cfg) {
    cfg.fold_on_bjd = foldsOnBjd(cfg);
    const raw = [
        ...buildDetectionSeries(cfg),
        ...buildNonDetectionSeries(cfg),
        ...buildForcedPhotSeries(cfg),
    ];
    const offset  = applyOffsetBands(raw, cfg);
    const limits  = buildLimitSeries(offset.length ? offset : raw);
    const series  = [...offset, ...limits];

    return {
        title:  { show: true, text: window.__LC_DATA__.objectName ?? cfg.oid, textStyle: { fontSize: 15, fontWeight: 500 } },
        textStyle: { fontFamily: CHART_FONT },
        tooltip: {},
        grid:   { left: 70, right: cfg.offset_bands ? '25%' : 30, top: 60, bottom: 40 },
        legend: buildLegend(cfg),
        xAxis:  {
            type: 'value', scale: true, splitLine: false,
            name: cfg.fold ? (cfg.fold_on_bjd ? 'Phase (BJD_TDB)' : 'Phase (MJD)') : 'MJD',
        },
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
// The periodogram can have ~100k periods, far more than the chart has pixels, and ECharts
// draws a scatter that big a few hundred points per frame (10 s or more). Keep the highest
// score in each of PERIODOGRAM_BINS bins, even in log period like the axis: the peaks, and
// the periods a click on them picks, are unchanged. It stays under ECharts' progressive
// threshold (3000 points), so the scatter is drawn in one frame.
const PERIODOGRAM_BINS = 1500;

function buildPeriodogramOptions() {
    const p           = rawPeriodogram;
    const bestSet     = new Set(p.best_periods_index ?? []);
    const periods     = p.periods ?? [];
    const best        = [];
    const binned      = new Map();
    let lo = Infinity, hi = -Infinity;
    for (const period of periods) { lo = Math.min(lo, period); hi = Math.max(hi, period); }
    const logLo = Math.log(lo), binWidth = (Math.log(hi) - logLo) / PERIODOGRAM_BINS || 1;

    for (let i = 0; i < periods.length; i++) {
        if (bestSet.has(i)) { best.push([periods[i], p.scores[i]]); continue; }
        const bin = Math.floor((Math.log(periods[i]) - logLo) / binWidth);
        if (!(binned.get(bin)?.[1] >= p.scores[i])) binned.set(bin, [periods[i], p.scores[i]]);
    }
    const regular = [...binned.values()];

    const opts = {
        tooltip:  { axisPointer: { type: 'cross' }, formatter: params => `<b>Period:</b> ${params.data[0]} <b>Score:</b> ${params.data[1]}` },
        grid:     { left: 70, right: '25%', top: 60, bottom: 40 },
        legend:   { left: 'right', top: 'middle', height: '80%', orient: 'vertical' },
        textStyle: { fontFamily: CHART_FONT },
        xAxis:    { type: 'log', name: 'Period [days]', scale: true, splitLine: false, min: '0.05', max: '500' },
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

    // Watch the chart's own box, not the plot grid: showing the periodogram shrinks the
    // light curve's container without changing the grid, and the canvas must follow it.
    new ResizeObserver(() => myChart?.resize()).observe(dom);

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
    // A period typed by the user is never meaningless, so it folds right away.
    const foldPending = config.fold && !(rawPeriodogram?.periods?.length) && !periodUserModified;
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
    setToggleLocked(document.querySelector('[name="periodogram_enabled"]'), !config.fold,
        'Turn on Fold to see the periodogram.');

    updateFoldNoPeriod();
    updateTotalHiddenHint();
    updateGroupModeNote();
    updatePeriodSource();
    updateChartStatus();

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

// ─── Fold without a period ────────────────────────────────────────────────────
// When the periodogram finds no period (or fails), the fold has nothing to use. Say so
// over the plot instead of leaving the previous chart on screen, until the user types
// a period of their own.
function updateFoldNoPeriod() {
    const box       = document.getElementById('fold-no-period');
    const text      = document.getElementById('fold-no-period-text');
    const container = document.getElementById('lightcurve-container');
    const hasPeriods = (rawPeriodogram?.periods?.length ?? 0) > 0;
    const show = config.fold && !hasPeriods && !periodogramLoading && periodogramStatus != null && !periodUserModified;

    if (show && text) {
        const manual = 'Type a period to fold the light curve manually.';
        if (periodogramStatus === 'failed') {
            text.textContent = `The period could not be computed. ${manual}`;
        } else {
            const survey = config.survey_id.toLowerCase();
            const members = periodogramObjects ? periodogramObjects.split(',') : [];
            const n = rawDetections.filter(d => d.survey_id.toLowerCase() === survey && d.variants?.mag_total).length
                + members.reduce((sum, k) => sum + (groupPhot.get(k)?.detections ?? []).filter(d => d.variants?.mag_total).length, 0);
            const which = members.length ? `this object and ${plural(members.length, 'other object')}` : 'this object';
            text.textContent = `No period found for ${which} (${plural(n, 'detection')} with total magnitude). ${manual}`;
        }
    }
    box?.classList.toggle('tw-hidden', !show);
    // Hide the previous (unfolded) chart behind the message rather than show it as if folded.
    container?.classList.toggle('tw-invisible', show);
}

// ─── Points without total magnitude ───────────────────────────────────────────
// In Total, points without a total magnitude (uncorrected ZTF) are left out of the chart.
// Say how many in a "?" next to the Diff/Total switch, shown only when some are hidden, so
// they don't silently disappear.
function updateTotalHiddenHint() {
    const hint = document.getElementById('total-hidden-hint');
    if (!hint) return;
    const parts = [];
    if (config.total && !isNotCorrected()) {
        for (const [items, type, label] of [
            [[...rawDetections, ...groupPoints('detections', config)],             'detections',        'detections'],
            [[...rawForcedPhotometry, ...groupPoints('forcedPhotometry', config)], 'forced_photometry', 'forced photometry points'],
        ]) {
            if (!(config.data_types ?? [type]).includes(type)) continue;
            const missing = items.filter(p => !pointValue(p, config)).length;
            if (missing) parts.push(`${missing} of ${items.length} ${label}`);
        }
    }
    hint.dataset.tip = parts.length ? `${parts.join(' and ')} have no total magnitude, so they are not shown.` : '';
    hint.classList.toggle('tw-hidden', !parts.length);
}

// ─── Locked toggles ───────────────────────────────────────────────────────────
// A disabled switch looks the same as an enabled one, so fade it, show a "not allowed"
// cursor and explain why on hover.
function setToggleLocked(el, locked, reason) {
    if (!el) return;
    el.disabled = locked;
    const label = el.closest('label');
    if (!label) return;
    // Fade everything but the "?" help, so its tooltip stays readable.
    for (const child of label.children) {
        if (!child.classList.contains('tw-group')) child.classList.toggle('tw-opacity-50', locked);
    }
    label.classList.toggle('tw-cursor-pointer', !locked);
    label.classList.toggle('tw-cursor-not-allowed', locked);
    if (locked) label.dataset.tipLocked = reason;
    else delete label.dataset.tipLocked;
}

// ─── Diff/Total toggle ────────────────────────────────────────────────────────
// Fold and external sources only work with total magnitude, so while either is on the
// switch is forced to Total and locked. Turning both off restores the user's choice.
// The other objects of the group don't lock it: they are drawn in whatever the user chose,
// with a warning of what each choice means across surveys (updateGroupModeNote).
function syncTotalToggle(form) {
    const el = form.querySelector('[name="total"]');
    if (!el) return;
    const needsTotal = (form.querySelector('[name="fold"]')?.checked ?? false)
        || (form.querySelector('[name="external_sources.enabled"]')?.checked ?? false);

    if (needsTotal && !el.disabled) {
        el.dataset.checkedBeforeLock = String(el.checked);
        el.checked = true;
    } else if (!needsTotal && el.disabled) {
        el.checked = el.dataset.checkedBeforeLock !== 'false';
    }
    setToggleLocked(el, needsTotal,
        'Fold and external sources use total magnitude. Turn them off to switch back to Diff.');
}

// ─── Object group: what Diff and Total mean across objects ────────────────────
// Neither view lines up exactly across surveys, so while other objects of the group are drawn, a note under
// the group switch says what to expect from the current one.
const GROUP_MODE_NOTES = {
    diff:  'Diff: each survey, and each ZTF field, subtracts its own template, so constant offsets between '
         + 'objects are expected. This is the view for transients.',
    total: 'Total: each survey measures with a different PSF, which takes in a different amount of host-galaxy '
         + 'light, so steps between surveys are expected for AGN and extended sources. For transients, use Diff.',
};

function updateGroupModeNote() {
    const note = document.getElementById('group-mode-note');
    if (!note) return;
    const shown = (config.group_selected?.length ?? 0) > 0;
    note.textContent = shown ? GROUP_MODE_NOTES[config.total ? 'total' : 'diff'] : '';
    note.classList.toggle('tw-hidden', !shown);
}

// ─── Object group switch ──────────────────────────────────────────────────────
// "Show on the light curve" gates the whole group: while it's off the checkboxes are disabled and faded,
// keeping what the user checked for when it's turned back on.
function groupEnabled(form) {
    return form.querySelector('[name="group.enabled"]')?.checked ?? false;
}

function syncGroupPanel(form) {
    const on = groupEnabled(form);
    for (const el of form.querySelectorAll('[name="group.objects[]"]')) el.disabled = !on;
    document.getElementById('group-panel')?.classList.toggle('lc-group-off', !on);
}

// ─── Non-detections toggle ────────────────────────────────────────────────────
// Non-detections are limiting magnitudes, so their checkbox is unavailable in flux view:
// unticked, greyed out and disabled. Going back to magnitude restores its previous state.
function syncNonDetectionsToggle(form) {
    const el = form.querySelector('[name="data_types[]"][value="non_detections"]');
    if (!el) return;
    const fluxOn = form.querySelector('[name="flux"]')?.checked ?? false;

    if (fluxOn && !el.disabled) {
        el.dataset.checkedBeforeFlux = String(el.checked);
        el.checked  = false;
        el.disabled = true;
    } else if (!fluxOn && el.disabled) {
        el.checked  = el.dataset.checkedBeforeFlux !== 'false';
        el.disabled = false;
    }

    const label = el.closest('label');
    for (const node of [label, el]) {
        node?.classList.toggle('tw-cursor-pointer', !fluxOn);
        node?.classList.toggle('tw-cursor-not-allowed', fluxOn);
    }
    label?.classList.toggle('tw-opacity-50', fluxOn);
    if (label && fluxOn) label.dataset.tipLocked = 'Limiting magnitudes are only shown in magnitude view.';
    else if (label) delete label.dataset.tipLocked;
}

// ─── Read config from form ────────────────────────────────────────────────────
function readConfigFromForm() {
    const form = document.getElementById('config-form');
    if (!form) return;

    const bool = name => form.querySelector(`[name="${name}"]`)?.checked ?? false;

    syncGroupPanel(form);
    syncTotalToggle(form);
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
    syncNonDetectionsToggle(form);
    config.data_types   = [...form.querySelectorAll('[name="data_types[]"]:checked')]  .map(el => el.value);
    if (groupInfo) {
        config.group_selected = groupEnabled(form)
            ? [...form.querySelectorAll('[name="group.objects[]"]:checked')].map(el => el.value)
            : [];
    }
}

// ─── Object group: fetch other objects' photometry on demand ─────────────────
// An object's photometry is fetched the first time it's drawn: when the group switch is turned on (the checked
// members), or when its checkbox is checked afterwards. A failure only leaves that object out of the chart.
async function loadGroupPhotometry() {
    const missing = (config.group_selected ?? []).filter(k => !groupPhot.has(k) && !groupLoading.has(k));
    if (!missing.length) return;
    missing.forEach(k => groupLoading.add(k));
    updateChartStatus();
    const infoAtStart = groupInfo;
    try {
        const apiUrl = window.__LC_DATA__.apiUrl;
        // The viewed object's position, so the members' BJD_TDB use the same one as its own points
        const position = config.meanra != null ? `&ra=${config.meanra}&dec=${config.meandec}` : '';
        const resp = await fetch(`${apiUrl}/htmx/group_photometry?objects=${encodeURIComponent(missing.join(','))}${position}`);
        if (!resp.ok) throw new Error(`group photometry: ${resp.status}`);
        const data = await resp.json();
        if (groupInfo !== infoAtStart) return;  // another object was loaded meanwhile
        for (const key of missing) groupPhot.set(key, { detections: [], forcedPhotometry: [] });
        const keyOf = p => `${p.survey_id.toLowerCase()}:${p.oid}`;
        for (const d of data.detections)        groupPhot.get(keyOf(d))?.detections.push(d);
        for (const f of data.forced_photometry) groupPhot.get(keyOf(f))?.forcedPhotometry.push(f);
    } catch (e) {
        console.error('Failed to load the photometry of the group:', e);
    } finally {
        missing.forEach(k => groupLoading.delete(k));
        updateChartStatus();
        updatePeriodSource();
        updateTotalHiddenHint();
        updateChart();
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
        if (periodEl) periodEl.value = config.period;
    } finally {
        settingPeriodProgrammatically = false;
    }
}

// ─── Lazy periodogram loader ──────────────────────────────────────────────────
// The associated objects drawn now, as the periodogram request names them.
function drawnObjectsKey() {
    return [...(config.group_selected ?? [])].sort().join(',');
}

// The periodogram is searched on the detections of the viewed object and of the other objects drawn at that moment.
// Fetched once, when Fold (or the periodogram) is first turned on; again only when the user asks ("Recompute",
// after changing the objects drawn). A recompute keeps the current periodogram and fold on screen until the new
// one arrives, and then folds at its best period, even over a period the user typed.
async function loadPeriodogram({ recompute = false } = {}) {
    if (periodogramLoading) return;
    if (!recompute && rawPeriodogram?.periods?.length) return;
    if (recompute) periodUserModified = false;
    periodogramLoading = true;
    const objects = drawnObjectsKey();
    const dataAtStart = window.__LC_DATA__;
    updateVisibility();
    try {
        const apiUrl = window.__LC_DATA__.apiUrl;
        const position = config.meanra != null ? `&ra=${config.meanra}&dec=${config.meandec}` : '';
        const members = objects ? `&objects=${encodeURIComponent(objects)}` : '';
        const r = await fetch(`${apiUrl}/htmx/periodogram?oid=${config.oid}&survey_id=${config.survey_id}${position}${members}`);
        if (!r.ok) throw new Error(r.status);
        const data = await r.json();
        if (window.__LC_DATA__ !== dataAtStart) return;  // another object was loaded meanwhile
        rawPeriodogram = data;
        periodogramObjects = objects;
        periodogramStatus = rawPeriodogram?.periods?.length ? null : 'empty';
        applyBestCandidatePeriod();
    } catch (e) {
        console.error('Periodogram load failed:', e);
        if (window.__LC_DATA__ === dataAtStart) periodogramStatus = 'failed';
    } finally {
        if (window.__LC_DATA__ === dataAtStart) {
            periodogramLoading = false;
            updateVisibility();
            updateChart();
        }
    }
}

function plural(n, word) {
    return `${n} ${word}${n === 1 ? '' : 's'}`;
}

// ─── Period source ────────────────────────────────────────────────────────────
// With a group, a line under the periodogram switch says which objects the period was searched on, and offers
// "Recompute" once the objects drawn differ from those.
function updatePeriodSource() {
    const row = document.getElementById('period-source-row');
    if (!row) return;
    const text   = document.getElementById('period-source');
    const button = document.getElementById('period-recompute');
    const hasPeriods = (rawPeriodogram?.periods?.length ?? 0) > 0;
    const searched   = periodogramLoading || hasPeriods || periodogramStatus != null;
    const hasOthers  = (groupInfo?.members?.length ?? 0) > 1 || (groupInfo?.nearby?.length ?? 0) > 0;
    const show = Boolean(config.fold && hasOthers && searched);
    row.classList.toggle('tw-hidden', !show);
    if (!show) return;

    const objectsText = (key, alone) => {
        const n = key ? key.split(',').length : 0;
        return n ? `this object and ${plural(n, 'other object')}` : alone;
    };
    const drawn = drawnObjectsKey();
    if (periodogramLoading) {
        text.textContent = `Searching the period on ${objectsText(drawn, 'this object')}…`;
    } else {
        const failed = periodogramStatus === 'failed' ? ' (recompute failed)' : '';
        text.textContent = `Period from ${objectsText(periodogramObjects, 'this object only')}${failed}`;
    }
    text.classList.toggle('lc-pulse', periodogramLoading);
    // Offered when the objects drawn changed, or to retry after a failure
    const stale = drawn !== periodogramObjects || periodogramStatus === 'failed';
    button.classList.toggle('tw-hidden', periodogramLoading || !stale);
}

// ─── Chart status ─────────────────────────────────────────────────────────────
// A small badge over the chart while something it will draw is on its way: the photometry of other objects, or a
// recomputed period (a first period has the full "Computing period…" overlay instead).
function updateChartStatus() {
    const el = document.getElementById('chart-status');
    if (!el) return;
    const messages = [];
    if (groupLoading.size) messages.push(`Loading ${plural(groupLoading.size, 'other object')}…`);
    if (config.fold && periodogramLoading && rawPeriodogram?.periods?.length) messages.push('Recomputing the period…');
    el.textContent = messages.join(' · ');
    el.classList.toggle('tw-hidden', !messages.length);
}

function onRecomputeClick(e) {
    if (!e.target.closest('#period-recompute')) return;
    loadPeriodogram({ recompute: true });
}

// ─── Side panel legend ────────────────────────────────────────────────────────
// The band chips stand in for the chart legend: each one gets the color of its
// series, from COLORS, so the colors live in one place. The text on a filled chip
// is dark or white, whichever reads better on that color.
function paintBandChips() {
    for (const el of document.querySelectorAll('.lc-band[data-survey][data-band]')) {
        const color = COLORS[el.dataset.survey]?.[el.dataset.band] ?? '#888888';
        const [r, g, b] = [1, 3, 5].map(i => parseInt(color.slice(i, i + 2), 16));
        el.style.setProperty('--lc-band', color);
        el.style.setProperty('--lc-band-fg', 0.299 * r + 0.587 * g + 0.114 * b > 150 ? '#1e1e1e' : '#ffffff');
    }
}

// ─── Two-way choices (Mag | Flux, Diff | Total) ───────────────────────────────
// Each button sets its side of the hidden checkbox, then fires the form's usual
// `change`. A locked (disabled) checkbox ignores them.
function onSegmentClick(e) {
    const button = e.target.closest('.lc-seg [data-seg]');
    if (!button) return;
    const input = button.closest('.lc-seg')?.querySelector('input[type="checkbox"]');
    if (!input || input.disabled) return;
    const checked = button.dataset.seg === 'on';
    if (input.checked === checked) return;
    input.checked = checked;
    input.dispatchEvent(new Event('change', { bubbles: true }));
}

// ─── Period steps ─────────────────────────────────────────────────────────────
// Folding is very sensitive to the period: an error dP shifts the phase by about T·dP/P² across a light
// curve that spans T days. So a step is a fraction of a cycle across the light curve, not a fraction of the
// period: dP = cycles·P²/T. ‹ › slide the fold 2% of a cycle, « » a tenth, at any period and time span.
function shownTimeSpan() {
    let min = Infinity, max = -Infinity;
    for (const list of [rawDetections, rawForcedPhotometry,
                        groupPoints('detections', config), groupPoints('forcedPhotometry', config)]) {
        for (const p of list ?? []) {
            if (p.mjd < min) min = p.mjd;
            if (p.mjd > max) max = p.mjd;
        }
    }
    return max > min ? max - min : 0;
}

function setPeriodFromControl(input, period) {
    if (!(period > 0)) return;
    input.value = String(Number(period.toPrecision(8)));
    input.dispatchEvent(new Event('change', { bubbles: true }));
}

function nudgePeriod(input, cycles) {
    const period = parseFloat(input.value);
    if (!(period > 0)) return;
    // Below one period of span, a cycle across the light curve is a cycle of the period itself.
    const span = Math.max(shownTimeSpan(), period);
    setPeriodFromControl(input, period + cycles * period * period / span);
}

function onPeriodButtonClick(e) {
    const button = e.target.closest('[data-period-step], [data-period-factor]');
    const input  = e.currentTarget.querySelector('[name="period"]');
    if (!button || !input) return;
    if (button.dataset.periodStep) nudgePeriod(input, parseFloat(button.dataset.periodStep));
    else setPeriodFromControl(input, parseFloat(input.value) * parseFloat(button.dataset.periodFactor));
}

function onPeriodKeydown(e) {
    if (e.target.name !== 'period' || (e.key !== 'ArrowUp' && e.key !== 'ArrowDown')) return;
    e.preventDefault();
    nudgePeriod(e.target, (e.key === 'ArrowUp' ? 1 : -1) * (e.shiftKey ? 0.1 : 0.02));
}

// ─── Group details ────────────────────────────────────────────────────────────
// "Details" shows a second line under each object: the pair's score and distance, and the object's detections.
function onGroupDetailsClick(e) {
    const button = e.target.closest('[data-group-details]');
    if (!button) return;
    const shown = document.getElementById('group-panel')?.classList.toggle('lc-show-meta') ?? false;
    button.setAttribute('aria-expanded', String(shown));
}

// ─── Help tooltips ────────────────────────────────────────────────────────────
// Any [data-tip] in the widget shows its text in one floating box on <body>, so
// the scrolling side panel never clips it. A locked control shows why instead
// (data-tip-locked, see setToggleLocked).
function bindTooltips() {
    let box = document.getElementById('lc-tip');
    if (!box) {
        box = document.createElement('div');
        box.id = 'lc-tip';
        box.setAttribute('role', 'tooltip');
        document.body.appendChild(box);
    }
    const show = e => {
        const el = e.target.closest?.('#main-app [data-tip], #main-app [data-tip-locked]');
        const text = el && (el.dataset.tipLocked || el.dataset.tip);
        if (!text) { box.style.display = 'none'; return; }
        box.textContent = text;
        box.style.display = 'block';
        const r = el.getBoundingClientRect();
        const w = box.offsetWidth, h = box.offsetHeight;
        const below = r.bottom + 6 + h <= window.innerHeight;
        box.style.top  = `${below ? r.bottom + 6 : Math.max(4, r.top - 6 - h)}px`;
        box.style.left = `${Math.min(Math.max(4, r.left), window.innerWidth - w - 4)}px`;
    };
    const hide = () => { box.style.display = 'none'; };
    document.addEventListener('mouseover', show);
    document.addEventListener('focusin', show);
    document.addEventListener('mouseout', e => {
        if (!e.relatedTarget || !e.target.closest?.('[data-tip], [data-tip-locked]')?.contains(e.relatedTarget)) hide();
    });
    document.addEventListener('focusout', hide);
    document.addEventListener('scroll', hide, true);
}

// ─── Init ─────────────────────────────────────────────────────────────────────
function init() {
    paintBandChips();
    initChart();
    updateVisibility();

    const form = document.getElementById('config-form');
    if (!form) return;
    syncNonDetectionsToggle(form);
    syncTotalToggle(form);

    // Debounce continuous inputs (sliders) slightly to avoid rebuilding on every tick.
    let debounceTimer = null;
    let prevExtEnabled       = config.external_sources?.enabled ?? false;
    let prevPeriodogramEnabled = config.periodogram_enabled;
    let prevFold             = config.fold;

    function onFormChange(e) {
        // The period input fires a bubbling `change` for direct edits and for the
        // step and X2 / /2 buttons (which dispatch change on the input). Treat those as
        // manual period changes — unless we set the value programmatically.
        if (e && e.target?.name === 'period' && !settingPeriodProgrammatically) {
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

        if (e?.target?.name === 'group.objects[]' || e?.target?.name === 'group.enabled') loadGroupPhotometry();
    }
    function onFormInput(e) {
        if (e.target.name === 'period' || e.target.name === 'offset_num') {
            // A user-driven period change pins the period — stop auto-adopting the
            // periodogram candidate. Programmatic updates set a guard so they don't.
            if (e.target.name === 'period' && !settingPeriodProgrammatically) {
                periodUserModified = true;
            }
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => { readConfigFromForm(); updateFoldNoPeriod(); updateChart(); }, 80);
        }
    }

    // This form is purely client-side (no action/method). Pressing Enter in a text
    // field (e.g. the period box) would otherwise trigger the browser's implicit
    // submit — a GET navigation to the current URL without oid/survey_id, which 422s
    // and tears down the widget. Block it; the period change already applied via `change`.
    form.addEventListener('submit', e => e.preventDefault());

    form.addEventListener('change', onFormChange);
    form.addEventListener('input',  onFormInput);
    form.addEventListener('click',  onSegmentClick);
    form.addEventListener('click',  onPeriodButtonClick);
    form.addEventListener('click',  onGroupDetailsClick);
    form.addEventListener('click',  onRecomputeClick);
    form.addEventListener('keydown', onPeriodKeydown);

    // Period selection from periodogram click — counts as a manual change.
    // Bound on `document` once per page: init() runs again on every HTMX swap, but
    // this listener (unlike the form listeners above, whose elements are replaced by
    // the swap) would otherwise stack up an extra copy per object change.
    if (!documentListenersBound) {
        documentListenersBound = true;
        bindTooltips();
        document.addEventListener('periodogram:periodSelected', e => {
            config.period = parseFloat(e.detail.period);
            periodUserModified = true;
            settingPeriodProgrammatically = true;
            try {
                const periodEl = document.querySelector('[name="period"]');
                if (periodEl) periodEl.value = config.period;
            } finally {
                settingPeriodProgrammatically = false;
            }
            updateFoldNoPeriod();
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

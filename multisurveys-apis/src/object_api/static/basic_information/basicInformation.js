const months = [
  "",
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
];
const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];


let binaryDisc = 0;
let binaryLast = 0;
let binaryRaDec = 0;

export function changeDiscoveryValue(discoveryDateMGD, discoveryDateMJD) {
  if (binaryDisc === 1) {
    document.getElementById("discoveryDate").innerHTML = discoveryDateMGD;
    document.getElementById("textDiscoveryToolTip").innerText = "View MJD";
    binaryDisc = 0;
  } else {
    document.getElementById("discoveryDate").innerHTML = discoveryDateMJD;
    document.getElementById("textDiscoveryToolTip").innerText = "View date";
    binaryDisc = 1;
  }
}

export function changeLastValue(lastDetectionMGD, lastDetectionMJD) {
  if (binaryLast === 1) {
    document.getElementById("lastDetection").innerHTML = lastDetectionMGD;
    document.getElementById("textLastDetectionToolTip").innerHTML = "View MJD";
    binaryLast = 0;
  } else {
    document.getElementById("lastDetection").innerHTML = lastDetectionMJD;
    document.getElementById("textLastDetectionToolTip").innerHTML = "View date";
    binaryLast = 1;
  }
}

export function changeRaDec(raDec, raDecTime) {
  if (binaryRaDec === 1) {
    document.getElementById("raDec").innerHTML = raDec;
    document.getElementById("textRaDecToolTip").innerHTML = "View H:M:S";
    binaryRaDec = 0;
  } else {
    document.getElementById("raDec").innerHTML = raDecTime;
    document.getElementById("textRaDecToolTip").innerHTML = "View Degrees";
    binaryRaDec = 1;
  }
}

export function jdToDate(mjd) {
  if (mjd === undefined || mjd === null || mjd === '') {
    return null
  }
  let date = (mjd - 40587) * 86400000
  date = new Date(date)

  let year = date.getUTCFullYear();
  let month = String(date.getUTCMonth() + 1);
  let day = String(date.getUTCDate()).padStart(2, '0');
  let hours = String(date.getUTCHours()).padStart(2, '0');
  let minutes = String(date.getUTCMinutes()).padStart(2, '0');
  let seconds = String(date.getUTCSeconds()).padStart(2, '0');
  let dayName = date.getUTCDay();

  return `${days[dayName]}, ${day} ${months[month]} ${year} ${hours}:${minutes}:${seconds} UTC`;
}


export function transformDec(dec, precision=2) {
  const sign = dec < 0 ? "-" : "+";
  dec = Math.abs(dec);
  const deg = Math.floor(dec);
  const decM = Math.abs(Math.floor((dec - deg) * 60));
  const decS = ((Math.abs((dec - deg) * 60) - decM) * 60).toFixed(precision);
  dec = `${sign}${deg}:${decM}:${decS}`;

  return dec;
}

export function transformRa(degrees, precision=3) {
  let degreesPerHour = 360 / 24;
  let hours = Math.floor(degrees / degreesPerHour);
  let minutes = Math.floor(((degrees % degreesPerHour) * 60) / degreesPerHour);
  let seconds = (
    (((degrees % degreesPerHour) * 3600) / degreesPerHour) %
    60
  ).toFixed(precision);

  let str = String(hours) + ":" + String(minutes) + ":" + String(seconds);

  return str;
}

export function setMenuUrl(ra, dec, measurement_id, object, raTime, decTime) {

  let raNed = encodeCoordinates(raTime)
  let decNed = encodeCoordinates(decTime)

  const urlDict = {
    "DESI Legacy Survey DR10": `https://www.legacysurvey.org/viewer/jpeg-cutout/?ra=${ra}&dec=${dec}&layer=ls-dr10&pixscale=0.1&bands=grz`,

    "NED": `https://ned.ipac.caltech.edu/conesearch?search_type=Near%20Position%20Search&in_csys=Equatorial&in_equinox=J2000&ra=${raNed}&dec=${decNed}&radius=0.17`,

    "PanSTARRS": `https://ps1images.stsci.edu/cgi-bin/ps1cutouts?pos=${ra}+${dec}&filter=color`,

    "SDSS DR18": `https://skyserver.sdss.org/dr18/en/tools/chart/navi.aspx?ra=${ra}8&dec=${dec}`,

    "SIMBAD": `https://simbad.u-strasbg.fr/simbad/sim-coo?Coord=${ra}%20${dec}&Radius.unit=arcsec&Radius=10`,

    "TNS": `https://www.wis-tns.org/search?ra=${ra}&decl=${dec}&radius=10&coords_unit=arcsec`,

    "Vizier": `https://vizier.cds.unistra.fr/viz-bin/VizieR-4?-c=${ra}+${dec}&-c.rs=10&-out.add=_r&-sort=_r&-out.max=$4`,

    "VSX": `https://www.aavso.org/vsx/index.php?view=results.get&coords=${ra}+${dec}&format=d&size=10&geom=r&unit=3&order=9`,
    
    "find-button-object": `https://findingchart.alerce.online/get_chart?oid=${object}&candid=${measurement_id}`,
  };


  for (let button in urlDict) {
    document.getElementById(button).href = urlDict[button];
  }
}


function encodeCoordinates(coordinate){
  return coordinate.replaceAll(":", "%3A")
}

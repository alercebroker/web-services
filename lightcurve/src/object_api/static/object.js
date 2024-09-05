import {
  changeDiscoveryValue,
  changeLastValue,
  changeRaDec,
  julianToGregorian,
  transformRa,
  transformDec,
  setMenuUrl,
} from "../static/basicInformation.js";

const FIXED_PRECISION = 7;
const objectInfo = JSON.parse(document.getElementById("object-data").text);

const object = objectInfo.object;
const corrected = objectInfo.corrected;
const stellar = objectInfo.stellar;
const detections = objectInfo.detections;
let discoveryDateMJD = objectInfo.discoveryDateMJD;
let lastDetectionMJD = objectInfo.lastDetectionMJD;
const nonDetections = objectInfo.nonDetections;
let ra = objectInfo.ra;
let dec = objectInfo.dec;
let candid = objectInfo.candid;

let raDec = `${Number.parseFloat(ra).toFixed(FIXED_PRECISION)}\n${Number.parseFloat(dec).toFixed(FIXED_PRECISION)}`;

let discoveryDateMGD = julianToGregorian(discoveryDateMJD);
let lastDetectionMGD = julianToGregorian(lastDetectionMJD);

let raTime = transformRa(ra);
let decTime = transformDec(dec);
let raDecTime = `${Number.parseFloat(raTime).toFixed(FIXED_PRECISION)}\n${Number.parseFloat(decTime).toFixed(FIXED_PRECISION)}`;

setMenuUrl(ra, dec, candid, object);

// En vez de usar variables binarias, podemos preguntar si es que esta en block o none y cambiar por el contrario.
// Tambien, si se ocupa la variable binaria, declararla antes.
function display_menu() {
  if (click === 0) {
    document.getElementById("menu-box").style.display = "block";
    click = 1;
  } else {
    document.getElementById("menu-box").style.display = "none";
    click = 0;
  }
}

document.getElementById("object").innerHTML = object;
document.getElementById("corrected").innerHTML = corrected;
document.getElementById("stellar").innerHTML = stellar;
document.getElementById("detections").innerHTML = detections;
document.getElementById("nonDetections").innerHTML = nonDetections;
document.getElementById("discoveryDate").innerHTML = discoveryDateMGD;
document.getElementById("lastDetection").innerHTML = lastDetectionMGD;
document.getElementById("raDec").innerHTML = raDec;

document
  .getElementById("changeDiscoveryValue")
  .addEventListener("click", () => {
    changeDiscoveryValue(discoveryDateMGD, discoveryDateMJD);
  });
document.getElementById("changeLastValue").addEventListener("click", () => {
  changeLastValue(lastDetectionMGD, lastDetectionMJD);
});
document.getElementById("changeRaDec").addEventListener("click", () => {
  changeRaDec(raDec, raDecTime);
});
let click = 0;
document
  .getElementById("menu-button")
  .addEventListener("click", () => display_menu());

function lastInformation(data) {
  let type, name, tnsLink, redshift;

  if (data.error) {
    type = name = redshift = "Error";
    tnsLink = "https://www.wis-tns.org/";
  } else if (typeof data === "object" && data !== null) {
    if (Object.keys(Object.values(data)[0] || {}).length > 25) {
      type = Object.values(data)[2] || "No disponible";
      name = Object.values(data)[1] || "No disponible";
      tnsLink = `https://www.wis-tns.org/object/${Object.values(data)[1] || ""}`;
      redshift = Object.values(Object.values(data)[0])[21] || "No disponible";
    } else {
      type = name = redshift = "-";
      tnsLink = "https://www.wis-tns.org/";
    }
  } else {
    type = name = redshift = "Respuesta inesperada";
    tnsLink = "https://www.wis-tns.org/";
  }

  document.getElementById("type").innerHTML = type;
  document.getElementById("name").innerHTML = name;
  document.getElementById("tns-link").href = tnsLink;
  document.getElementById("redshift").innerHTML = redshift;
}

const myClick = document.getElementById("menu-button");

function handleOutsideClick(event) {
  if (!myClick.contains(event.target)) {
    click = 1;
    display_menu();
  }
}

document.addEventListener("click", handleOutsideClick);

await fetch("https://tns.alerce.online/search", {
  headers: {
    accept: "application/json",
    "cache-control": "no-cache",
    "content-type": "application/json",
  },
  body: '{"ra":' + String(ra) + ',"dec":' + String(dec) + "}",
  method: "POST",
  mode: "cors",
})
  .then((response) => {
    return response.text();
  })
  .then((text) => {
    if (text.includes("Error message")) {
      throw new Error(text);
    }
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  })
  .then((data) => {
    lastInformation(data);
  })
  .catch((error) => {
    lastInformation({
      error: true,
      message: error.message,
    });
  });

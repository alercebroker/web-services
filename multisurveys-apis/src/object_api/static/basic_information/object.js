import {
  changeDiscoveryValue,
  changeLastValue,
  changeRaDec,
  jdToDate,
  transformRa,
  transformDec,
  setMenuUrl,
} from "./basicInformation.js";

const FIXED_PRECISION = 7;


export function init() {


  let objectInfo = JSON.parse(document.getElementById("object-data").text);

  let object = objectInfo.object;
  let corrected = objectInfo.corrected;
  let stellar = objectInfo.stellar;
  let detections = objectInfo.detections;
  let discoveryDateMJD = objectInfo.discoveryDateMJD;
  let lastDetectionMJD = objectInfo.lastDetectionMJD;
  let nonDetections = objectInfo.nonDetections;
  let ra = objectInfo.ra;
  let dec = objectInfo.dec;
  let candid = objectInfo.candid;

  let raDec = `${Number.parseFloat(ra).toFixed(FIXED_PRECISION)}<br>${Number.parseFloat(dec).toFixed(FIXED_PRECISION)}`;

  let discoveryDateMGD = formatDate(discoveryDateMJD);
  let lastDetectionMGD = formatDate(lastDetectionMJD);

  let raTime = transformRa(ra, 3);
  let decTime = transformDec(dec, 2);

  let raDecTime = `${raTime}<br>${decTime}`;

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
  document.getElementById("menu-button-object").addEventListener("click", () => display_menu());
  document.getElementById("menu-box-object").addEventListener("click", () => display_menu());

  setMenuUrl(ra, dec, candid, object, raTime, decTime);
}


export function elementReady(selector) {
  return new Promise((resolve, reject) => {
    const el = document.querySelector(selector);
    if (el) {
      resolve(el);
    }

    new MutationObserver((mutationRecords, observer) => {
      Array.from(document.querySelectorAll(selector)).forEach(element => {
        resolve(element);
        observer.disconnect();
      });
    })
    .observe(document.documentElement, {
      childList: true,
      subtree: true
    });
  });
}

function formatDate(val){
  return jdToDate(val)
}

let click = 0
function display_menu() {
  let menu = document.getElementById("menu-box-object")
  if(menu.classList.contains("tw-hidden")){
    menu.classList.remove("tw-hidden")
  } else {
    menu.classList.add("tw-hidden")
  }
}


function handleOutsideClick(event) {
  let myClick = document.getElementById("menu-button-object");
  if (myClick && !myClick.contains(event.target)) {
    click = 1;
    display_menu();
  }
}

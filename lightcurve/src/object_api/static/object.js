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


export function init() {


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

  let raDec = `${Number.parseFloat(ra).toFixed(FIXED_PRECISION)}<br>${Number.parseFloat(dec).toFixed(FIXED_PRECISION)}`;

  let discoveryDateMGD = julianToGregorian(discoveryDateMJD);
  let lastDetectionMGD = julianToGregorian(lastDetectionMJD);

  let raTime = transformRa(ra, 3);
  let decTime = transformDec(dec, 2);

  let listRaTime = raTime.split(':');
  let listDecTime = decTime.split(':');
  
  // Pasamos los dos puntos (:) a su version codificada de URL (%3A)
  let newRaTime = listRaTime.join('%3A');
  let newDecTime = listDecTime.join('%3A');
  
  let raDecTime = `${raTime}<br>${decTime}`;
  
  setMenuUrl(ra, dec, candid, object, newRaTime, newDecTime);

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
  document.getElementById("copyButton").addEventListener("click", ()=> {
    copyFunction();
  })
  document
    .getElementById("menu-button")
    .addEventListener("click", () => display_menu());

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

// En vez de usar variables binarias, podemos preguntar si es que esta en block o none y cambiar por el contrario.
// Tambien, si se ocupa la variable binaria, declararla antes.
let click = 0;
function display_menu() {
  if (click === 0) {
    document.getElementById("menu-box").style.display = "block";
    click = 1;
  } else {
    document.getElementById("menu-box").style.display = "none";
    click = 0;
  }
}


function handleOutsideClick(event) {
  let myClick = document.getElementById("menu-button");
  if (myClick && !myClick.contains(event.target)) {
    click = 1;
    display_menu();
  }
}

function copyFunction() {
  const element = document.getElementById('raDec');
  if (!element) {
    console.error('Element with id "raDec" not found');
    return false;
  }

  let text = element.innerText || element.textContent;
  text = text.replace(/\s+/g, ' ').trim();
  text = text.replace(/(\d+\.\d+)(?:\s*)(\d+\.\d+)/, '$1 $2');

  navigator.clipboard.writeText(text).then(
    () => {
      document.getElementById('textCopyButton').innerHTML = 'Copied!';
      setTimeout(() => {
        document.getElementById('textCopyButton').innerHTML = 'Copy to clipboard';
      }, 2000); 
    },
    (err) => {
      console.error('Failed to copy text:', err);
      document.getElementById('textCopyButton').innerHTML = 'Copy failed';
    }
  );

  return true;
}
document.addEventListener("click", handleOutsideClick);
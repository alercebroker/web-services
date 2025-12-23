

export function downloadStamp(stampType, buttonElement) {
  const imageIdMap = {
    "science": "scienceImg",
    "template": "templateImg",
    "difference": "differenceImg"
  }

  const imgElement = document.getElementById(imageIdMap[stampType])
  if (!imgElement) {
    console.error(`Image element not found for stamp type: ${stampType}`)
    return
  }

  const oidMid = buttonElement.getAttribute("content")
  const dataUrl = imgElement.src
  const link = document.createElement("a")
  link.href = dataUrl
  link.download = `${oidMid}_${stampType}.png`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

export function init() {

  // Download button elements
  let scienceDownload = document.getElementById("scienceDownload")
  let templateDownload = document.getElementById("templateDownload")
  let differenceDownload = document.getElementById("differenceDownload")

  // MJD dropdown arrow elements
  let mjdArrowWrapper = document.getElementById("mid_arrow");
  let selectElement = document.getElementById("measurement_id");

  // Zoom image elements
  let scienceZoom = document.getElementById("scienceZoom");
  let templateZoom = document.getElementById("templateZoom");
  let differenceZoom = document.getElementById("differenceZoom");
  let imagesZoom = [scienceZoom, templateZoom, differenceZoom];
  // Zoom button elements
  let zoomStamps = document.getElementById("zoomStamp")

  // Download button eventListeners 
  scienceDownload.addEventListener("click", () => downloadStamp("science", scienceDownload))
  templateDownload.addEventListener("click", () => downloadStamp("template", templateDownload))
  differenceDownload.addEventListener("click", () => downloadStamp("difference", differenceDownload))

  // MJD dropdown arrow eventListeners
  selectElement.addEventListener("mousedown", () => {
    set_arrow_direction(mjdArrowWrapper);
  });
  selectElement.addEventListener("mouseup", () => {
    set_arrow_direction(mjdArrowWrapper);
  });

  for (let zoomElement of imagesZoom) {
    // Zoom image eventListeners
    console.log(zoomElement)
    zoomElement.addEventListener('mousemove', (event) => {
      zoomElement.style.setProperty('--display', 'block');

      let rect = zoomElement.getBoundingClientRect();

      let pointer = {
        x: ((event.clientX - rect.left) * 100) / rect.width,
        y: ((event.clientY - rect.top) * 100) / rect.height
      }

      zoomElement.style.setProperty('--zoom-x', pointer.x + '%');
      zoomElement.style.setProperty('--zoom-y', pointer.y + '%');

    })
    zoomElement.addEventListener('mouseleave', () => {
      zoomElement.style.setProperty('--display', 'none');
    })
  }

  // Zoom button eventListeners
  zoomStamps.addEventListener('click', () => {
    let currentVal = getComputedStyle(scienceZoom).getPropertyValue('--z-index').trim();

    if (parseInt(currentVal) > 0) {
      scienceZoom.style.setProperty('--z-index', -1)
      templateZoom.style.setProperty('--z-index', -1)
      differenceZoom.style.setProperty('--z-index', -1)
    } else {

      scienceZoom.style.setProperty('--z-index', 1)
      templateZoom.style.setProperty('--z-index', 1)
      differenceZoom.style.setProperty('--z-index', 1)
    }
  })
}

function set_arrow_direction(container) {
  let svg = container.querySelector('svg[name="arrow_icon"]');
  if (!svg) return;

  let path = svg.querySelector('path');

  let currentDirection = svg.dataset.direction;

  if (currentDirection === "down") {
    svg.dataset.direction = 'up';
    path.setAttribute('d', "M480-528 296-344l-56-56 240-240 240 240-56 56-184-184Z");
  } else {
    svg.dataset.direction = 'down';
    path.setAttribute('d', "M480-344 240-584l56-56 184 184 184-184 56 56-240 240Z");
  }

}





















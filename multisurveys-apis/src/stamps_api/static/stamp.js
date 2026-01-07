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
  const dataUrl = imgElement.getAttribute("content")
  const link = document.createElement("a")
  link.href = dataUrl
  link.download = `${oidMid}_${stampType}.fits.gz`
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

  // Crosshair image elements
  let stampsContainer = document.getElementById('stampsContainer')

  // Crosshair button elements
  let crossHair = document.getElementById('crossHairStamps')

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

  // Function to connect mouseover functionality into the 3 stamps when zoom is activated.
  makeZoomWork(imagesZoom)

  // Zoom button eventListeners
  zoomStamps.addEventListener('click', () => {
    toggleZoom()
    if (!stampsContainer.classList.contains('hide-crosshairs')) {
      stampsContainer.classList.toggle('hide-crosshairs')
    }
  })

  // Crosshair buttom eventListeners
  crossHair.addEventListener('click', () => {
    stampsContainer.classList.toggle('hide-crosshairs')
    toggleZoom(true)
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

function makeZoomWork(imagesZoom) {

  for (let zoomElement of imagesZoom) {
    // Zoom image eventListeners
    zoomElement.addEventListener('mousemove', (event) => {
      scienceZoom.style.setProperty('--display', 'block');
      templateZoom.style.setProperty('--display', 'block');
      differenceZoom.style.setProperty('--display', 'block');
      let rect = zoomElement.getBoundingClientRect();

      let pointer = {
        x: ((event.clientX - rect.left) * 100) / rect.width,
        y: ((event.clientY - rect.top) * 100) / rect.height
      }

      scienceZoom.style.setProperty('--zoom-x', pointer.x + '%');
      templateZoom.style.setProperty('--zoom-x', pointer.x + '%');
      differenceZoom.style.setProperty('--zoom-x', pointer.x + '%');

      scienceZoom.style.setProperty('--zoom-y', pointer.y + '%');
      templateZoom.style.setProperty('--zoom-y', pointer.y + '%');
      differenceZoom.style.setProperty('--zoom-y', pointer.y + '%');

    })
    zoomElement.addEventListener('mouseleave', () => {
      scienceZoom.style.setProperty('--display', 'none');
      templateZoom.style.setProperty('--display', 'none');
      differenceZoom.style.setProperty('--display', 'none');
    })

  }
}

function toggleZoom(crossFlag = false) {

  let currentVal = getComputedStyle(scienceZoom).getPropertyValue('--z-index').trim();

  if (parseInt(currentVal) > 0 || crossFlag) {
    scienceZoom.style.setProperty('--z-index', -1)
    templateZoom.style.setProperty('--z-index', -1)
    differenceZoom.style.setProperty('--z-index', -1)
    crossFlag = false
  } else {
    scienceZoom.style.setProperty('--z-index', 1)
    templateZoom.style.setProperty('--z-index', 1)
    differenceZoom.style.setProperty('--z-index', 1)
  }
}



















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
  let imageZoom = document.getElementById("imageZoom");

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

  // Zoom image eventListeners
  imageZoom.addEventListener('mousemove', (event) => {
    imageZoom.style.setProperty('--display', 'block');

    let rect = imageZoom.getBoundingClientRect();

    let pointer = {
      x: ((event.clientX - rect.left) * 100) / rect.width,
      y: ((event.clientY - rect.top) * 100) / rect.height
    }

    imageZoom.style.setProperty('--zoom-x', pointer.x + '%');
    imageZoom.style.setProperty('--zoom-y', pointer.y + '%');

  })
  imageZoom.addEventListener('mouseleave', () => {
    imageZoom.style.setProperty('--display', 'none');
  })

  // Zoom button eventListeners
  zoomStamps.addEventListener('click', () => {
    let currentVal = getComputedStyle(imageZoom).getPropertyValue('--z-index').trim();

    if (parseInt(currentVal) > 0) {
      imageZoom.style.setProperty('--z-index', -1)
    } else {
      imageZoom.style.setProperty('--z-index', 1)
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





















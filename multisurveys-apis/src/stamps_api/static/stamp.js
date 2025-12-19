let scienceDownload = document.getElementById("scienceDownload")
let templateDownload = document.getElementById("templateDownload")
let differenceDownload = document.getElementById("differenceDownload")

scienceDownload.addEventListener("click", () => downloadStamp("science", scienceDownload))
templateDownload.addEventListener("click", () => downloadStamp("template", templateDownload))
differenceDownload.addEventListener("click", () => downloadStamp("difference", differenceDownload))

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

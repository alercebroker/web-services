

let scienceDownload = document.getElementById("scienceDownload")
let templateDownload = document.getElementById("templateDownload")
let differenceDownload = document.getElementById("differenceDownload")

scienceDownload.addEventListener("click", () => downloadStamp("science"))
templateDownload.addEventListener("click", () => downloadStamp("template"))
differenceDownload.addEventListener("click", () => downloadStamp("difference"))

export function downloadStamp(stampType) {
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

    const dataUrl = imgElement.src
    const link = document.createElement("a")
    link.href = dataUrl
    link.download = `stamp_${stampType}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
}

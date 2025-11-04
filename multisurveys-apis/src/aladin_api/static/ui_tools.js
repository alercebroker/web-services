

export function draw(source, canvasCtx, viewParams) {
    canvasCtx.beginPath()
    canvasCtx.arc(
      source.x,
      source.y,
      source.data.size * 2,
      0,
      2 * Math.PI,
      false
    )
    canvasCtx.closePath()
    canvasCtx.strokeStyle = '#c38'
    canvasCtx.lineWidth = 3
    canvasCtx.globalAlpha = 0.7
    canvasCtx.stroke()
    const fov = Math.max(viewParams.fov[0], viewParams.fov[1])
    // object name is displayed only if fov<10°
    if (fov > 10) {
      return
    }
    canvasCtx.globalAlpha = 0.9
    canvasCtx.globalAlpha = 1
    const xShift = 20
    canvasCtx.font = '15px Arial'
    canvasCtx.fillStyle = '#eee'
    canvasCtx.fillText(source.data.name, source.x + xShift, source.y - 4)
    // object type is displayed only if fov<2°
    if (fov > 2) {
      return
    }
    canvasCtx.font = '12px Arial'
    canvasCtx.fillStyle = '#abc'
    canvasCtx.fillText(source.data.class, source.x + 2 + xShift, source.y + 10)
}
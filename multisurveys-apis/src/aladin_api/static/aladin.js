
let aladin

export function init(A) {
    
    A.init.then(() => {
        aladin = A.aladin('#aladin-lite-div', 
            {
                survey: 'P/PanSTARRS/DR1/color-z-zg-g',
                fov: 0.01, 
                cooFrame: 'J2000d', 
            }
        );
    });

    aladin.view.reticleCanvas.onwheel = customZoom
}

function customZoom(event){
    event.preventDefault()
    event.stopPropagation()

    console.log("hola")

    let level = aladin.view.zoomLevel
    let delta = -event.deltaY

    if(delta > 0){
        level += 1
    } else {
        level -= 1
    }

    aladin.view.setZoomLevel(level)

    return false
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
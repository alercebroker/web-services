import { draw } from "./ui_tools.js";


let aladin

export async function init(A) {
  let raw_data = JSON.parse(document.getElementById("aladin-data").text);
  let objects = raw_data.objects
  let selected_object = raw_data.selected_object
  let catalog = null


  await A.init
  aladin = A.aladin('#aladin-lite-div', 
      {
          survey: 'P/PanSTARRS/DR1/color-z-zg-g',
          fov: 0.01, 
          cooFrame: 'J2000d', 
      }
  );

  if(objects){
    catalog = addObjects(aladin, objects)
  }

  on_selected_object_change(selected_object, aladin, catalog)
  console.log(aladin.view.aladinDiv)
  // aladin.addEventListener('wheel', customZoom, {passive: false });

}


function addObjects(aladin, objects){
  aladin.removeLayers()

  let sources = []
  objects.forEach((object) => {
    sources.push(
      A.source(object.meanra, object.meandec, {
        name: object.oid,
        size: 2,
        class: ''
      })
    )  
  })

  let catalog = A.catalog({ sourceSize: 10, shape: draw})
  catalog.addSources(sources)
  aladin.addCatalog(catalog)

  // aladin.on('objectClicked', this.onCLick)

  return catalog
}

function on_selected_object_change(view_object, aladin, catalog){

  let coordinates = {
    ra: view_object.meanra,
    dec: view_object.meandec
  }

  add_catalogs_information(coordinates)

  let src = catalog.sources.find((source) => {
    return source.data.name === view_object.oid
  })


  on_aladin_object_change(src)
  aladin.gotoRaDec(coordinates.ra, coordinates.dec)
}


function add_catalogs_information(coordinates) {
  // if (!this.showCloseObjects || !this.aladin) {
  //   return
  // }
  aladin.addCatalog(
    A.catalogFromSimbad(coordinates, 0.014, {
      onClick: 'showTable',
    })
  )
  aladin.addCatalog(
    A.catalogFromNED(coordinates, 0.014, {
      onClick: 'showTable',
      shape: 'plus',
    })
  )
  aladin.addCatalog(
    A.catalogFromVizieR('I/311/hip2', coordinates, 0.014, {
      onClick: 'showTable',
    })
  )
}

function on_aladin_object_change(new_object){
  new_object.select()
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
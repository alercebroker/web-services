import { draw } from "./ui_tools.js";


class creatorAladin {

  constructor(aladin, catalog, objects){
    this._aladin = aladin
    this._catalog = catalog
    this._objects = objects
    this.sources = []
  }

  get aladin(){
    return this._aladin
  }

  get objects(){
    return this._objects
  }

  get catalog(){
    return this._catalog
  }

  set_sources(new_sources){
    this._aladin.removeLayers()
    this.sources = new_sources
  }

  create_catalog(config){
    this._catalog = config
    this._catalog.addSources(this.sources)
    this._aladin.addCatalog(this._catalog)
  }

  add_catalog_information(new_catalog) {
    this._aladin.addCatalog(new_catalog)
  }

}


export async function init(A) {
  let raw_data = JSON.parse(document.getElementById("aladin-data").text);
  let objects = raw_data.objects
  let selected_object = raw_data.selected_object
  let catalog = null
  let new_object = null
  let aladin = null
  let aladin_instance = null


  await A.init
  aladin = A.aladin('#aladin-lite-div', 
      {
          survey: 'P/PanSTARRS/DR1/color-z-zg-g',
          fov: 0.01, 
          cooFrame: 'J2000d', 
      }
  );

  aladin_instance = new creatorAladin(aladin, catalog, objects)

  if(objects){
    let catalog_config = A.catalog({ sourceSize: 10, shape: draw})
    let new_source = create_source(aladin_instance)

    aladin_instance.set_sources(new_source)
    aladin_instance.create_catalog(catalog_config)

    aladin_instance.aladin.on('objectClicked', (event) => {
      if(event?.catalog?.name == "catalog"){
        new_object = find_object_in_catalog(event, aladin_instance)
        on_selected_object_change(new_object, aladin_instance)
      }
    })
  }

  on_selected_object_change(selected_object, aladin_instance)
  // aladin.addEventListener('wheel', customZoom, {passive: false });

}

function create_source(aladin){
  let new_source = []

  aladin.objects.forEach((object) => {
    new_source.push(
      A.source(object.meanra, object.meandec, {
        name: object.oid,
        size: 2,
        class: ''
      })
    )  
  })

  return new_source
}

function find_object_in_catalog(object_selected, aladin){
  let found_object = aladin.objects.find((object) => {
    return object.oid === object_selected.data.name
  })

  if(!found_object){
    return null
  }

  return {'oid': found_object.oid, 'meanra': found_object.meanra, 'meandec': found_object.meandec }
}

function on_selected_object_change(view_object, aladin){
  let coordinates = { ra: view_object.meanra, dec: view_object.meandec }

  add_catalogs_information(aladin, coordinates)
  unselect_old_object(aladin)
  select_new_object_by_oid(aladin, view_object.oid)


  aladin._aladin.gotoRaDec(coordinates.ra, coordinates.dec)
}


function unselect_old_object(aladin){
  aladin.catalog.deselectAll()
}

function select_new_object_by_oid(aladin_instace, selected_oid){
  let find_new_object = aladin_instace.catalog.sources.find((source) => {
    if(source.data.name === selected_oid){
      return source
    }
  })

  if(find_new_object){
    find_new_object.select()
  }
}

function add_catalogs_information(aladin, coordinates){
  if (!aladin) {
    return
  }

  let  simbad_catalog = A.catalogFromSimbad(coordinates, 0.014, { onClick: 'showTable', })
  let  ned_catalog = A.catalogFromNED(coordinates, 0.014, { onClick: 'showTable', shape: 'plus', })
  let vizier_catalog = A.catalogFromVizieR('I/311/hip2', coordinates, 0.014, { onClick: 'showTable', })

  aladin.add_catalog_information(simbad_catalog)
  aladin.add_catalog_information(ned_catalog)
  aladin.add_catalog_information(vizier_catalog)

}

function customZoom(event){
  event.preventDefault()
  event.stopPropagation()

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
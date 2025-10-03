

export function init(){
  window.prepare_params = prepare_params
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

function prepare_params(evt){
  let url = new URL(evt.detail.headers['HX-Current-URL'])

  if(evt.detail.elt.getAttribute("name") == "side_objects_btn"){
    let next_page = evt.detail.elt.dataset.next

    url.searchParams.set("page", next_page)
  }else{
    let selected_oid = evt.detail.elt.dataset.oid
    let current_page = document.getElementById('current_page').dataset.page

    url.searchParams.set("selected_oid", selected_oid)
    url.searchParams.set("page", current_page)
  }

  evt.detail.parameters = {...prepare_data(url)}

}

function prepare_data(url){
    let dict_params = get_params_url(url)

    return  dict_params
}


function get_params_url(url){
  let params = new URLSearchParams(url.search)
  let form_dict = {}

  params.forEach((value, key) => {
    if(key == "oid"){
      form_dict[key] = params.getAll("oid")
    } else {
      form_dict[key] = value
    }
  })

  return form_dict
}
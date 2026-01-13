

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
  let page = get_page(evt.detail.elt)
  let selected_oid = evt.detail.elt.dataset.oid

  url.searchParams.set("page", page)
  url.searchParams.set("selected_oid", selected_oid)

  evt.detail.parameters = {...prepare_data(url)}
}

function get_page(event_element){
  let current_page = document.getElementById('current_page').dataset.page
  
  if (event_element.getAttribute("name") == "side_objects_btn"){
    return event_element.dataset.next
  }

  return current_page
}

function prepare_data(url){
    let dict_params = get_params_url(url)

    return  dict_params
}


function get_params_url(url){
  let params = new URLSearchParams(url.search)
  let form_dict = {}

  params.forEach((value, key) => {
    if (key === 'oid' || key === 'n_det' || key === 'firstmjd') {
      form_dict[key] = params.getAll(key)
    } else {
      form_dict[key] = value
    }
  })

  return form_dict
}

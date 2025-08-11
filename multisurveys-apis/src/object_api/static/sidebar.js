

export function init(){

  document.body.addEventListener('htmx:configRequest', function(evt){
    let element_name = evt.detail.elt.getAttribute("name")

    if(element_name == "sidebar-row-element"){
      evt.detail.parameters = {...prepare_data(), "selected_oid":evt.detail.elt.dataset.oid}
    }

    if(element_name == "prev_page_sidebar" || element_name == "next_page_sidebar"){
      evt.detail.parameters = {...prepare_data(evt.detail.elt.dataset.next)}
    }
  })
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

function prepare_data(next_page = false){
    let dict_params = get_params_url(document.location.search)

    if(next_page){
      dict_params["page"] = next_page
    }

    return  dict_params
}


function get_params_url(url){
    let params = new URLSearchParams(url)
    let form_dict = {}

    params.forEach((value, key) => {
        form_dict[key] = value
    })

    return form_dict
}


export function init(){
    window.request_data = request_data 
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

function request_data(next_page){
    let dict_params = get_params_url(document.location.search)

    dict_params["page"] = next_page

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
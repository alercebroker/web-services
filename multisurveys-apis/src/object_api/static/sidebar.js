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

export function init(){
  window.prepare_params = prepare_params
  window.highlight_new_object = highlight_new_object
}

function highlight_new_object(event) {
  let clicked_oid = event.srcElement

  unhighlight_selected_object()
  select_element(clicked_oid)
}

function unhighlight_selected_object(){
  let currently_selected = document.querySelector('.obj-selected-item')

  if (check_if_no_item_is_selected(currently_selected)) {
    return
  }

  deselect_element(currently_selected)
}

function select_element(element) {
  element.classList.replace('obj-unselected-item', 'obj-selected-item',)
}

function deselect_element(element) {
  element.classList.replace('obj-selected-item', 'obj-unselected-item')
}

function check_if_no_item_is_selected(object) {
  return !object
}

function prepare_params(evt){
  let url = new URL(evt.detail.headers['HX-Current-URL'])
  let page = get_page(evt.detail.elt)
  let selected_oid = get_selected_oid()

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

function get_selected_oid(){
  let selected = document.querySelector('.obj-selected-item')

  if(check_if_no_item_is_selected(selected)) {
    return document.getElementById('selected_oid_cache').value
  }

  return selected.dataset.oid
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

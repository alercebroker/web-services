import { check_if_no_item_is_selected } from "./conditions.js";


export function prepare_params(evt){
    let url = new URL(evt.detail.headers['HX-Current-URL'])
    let page = get_page(evt.detail.elt)
    let selected_oid = get_selected_oid()
  
    url.searchParams.set("page", page)
    url.searchParams.set("selected_oid", selected_oid)
  
    evt.detail.parameters = {...get_params_url(url)}
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
  
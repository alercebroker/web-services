import { check_if_no_item_is_selected } from "./conditions.js"


export function highlight_new_object(event) {
    console.log("hola desde highlight")
    unhighlight_selected_object()
    select_element(event.srcElement)
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
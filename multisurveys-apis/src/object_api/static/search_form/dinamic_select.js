import { clean_nodes_in_dom } from "../ui_helpers.js";


export function create_dinamic_dropdown() {
    // se seleccionan todos los dropdowns
    for (const dropdown of document.querySelectorAll(".obj-select-wrapper")) {
        dropdown.addEventListener('click', function () {
            this.querySelector('.obj-select').classList.toggle('open');
        })
    }

    // Se incorporan funcionalidad a las opciones de los dropdowns
    for (const option of document.querySelectorAll(".obj-custom-option")) {
        option.addEventListener('click', () => {
            if (!option.classList.contains('obj-selected')) {

            option.parentNode.querySelector('.obj-custom-option.obj-selected').classList.remove('obj-selected');

            option.classList.add('obj-selected');

            option.closest('.obj-select').querySelector('.obj-select__trigger span').textContent = option.textContent;

            if (!option.closest('.obj-select').querySelector('.obj-select__trigger span').classList.contains('dark:tw-text-[#EEEEEE]')) {
                option.closest('.obj-select').querySelector('.obj-select__trigger span').classList.add('dark:tw-text-[#EEEEEE]')
            }


            option.closest('.obj-select').querySelector('.obj-select__trigger span').setAttribute("data-classes", option.getAttribute("data-classes"));
            option.closest('.obj-select').querySelector('.obj-select__trigger span').setAttribute("data-classifier", option.getAttribute("data-classifier"));
            option.closest('.obj-select').querySelector('.obj-select__trigger span').setAttribute("data-version", option.getAttribute("data-version"));



            if (option.closest('.obj-select').querySelector('.obj-select__trigger span').id == "classifier") {
                document.getElementById("classifier").dispatchEvent(new Event("change"))
            }
            }
        })
    }
}


export function add_classifiers_items_functionality(selected, options) {

    for (let item of options.querySelectorAll(".obj-custom-option")) {

        item.addEventListener('click', () => {

            withdraw_selected_item(options)
            change_selected_item(item)

            selected.textContent = item.textContent;

            selected.setAttribute("data-classes", item.getAttribute("data-classes"));
            selected.setAttribute("data-classifier", item.getAttribute("data-classifier"));
            
            dropdown_class_configure(item.getAttribute("data-classes"))
        })
    }


}


function draw_classes_options(classes) {
    let classes_options = document.getElementById("classes_options")
    let classes_arr = classes.split(",")

    classes_arr.forEach((class_name, index) => {
        let new_option = document.createElement("a")
        new_option.href = "#"
        new_option.textContent = class_name
        new_option.dataset.value = class_name
        new_option.classList.add("obj-custom-option", "hover:tw-bg-[#b2b2b2]")

        classes_options.appendChild(new_option)
    })
    
}


function dropdown_class_configure(classes) {
    clean_nodes_in_dom(document.getElementById("classes_options"))
    draw_classes_options(classes)
    add_class_items_functionality(document.getElementById("classes_options"))
}


function add_class_items_functionality(options) {

    let selected = document.getElementById("class_selected")

    for (let item of options.querySelectorAll(".obj-custom-option")) {

        item.addEventListener('click', () => { 
            withdraw_selected_item(options)
            change_selected_item(item)
            selected.textContent = item.textContent;
            selected.setAttribute("data-value", item.getAttribute("data-value"));
        })
    }
}

function withdraw_selected_item(options) {
    for (let item of options.querySelectorAll(".obj-custom-option")) {
        if (item.classList.contains('obj-selected')) {
            item.classList.remove('obj-selected');
        }
    }
}


function change_selected_item(item) {
    item.classList.add('obj-selected');
}
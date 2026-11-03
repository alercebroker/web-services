import { draw_dropdown_options } from "../draw_elements.js";
import { clean_nodes_in_dom, switch_arrow_icon } from "../ui_helpers.js";
import { draw_classes_options, draw_empty_option } from "../draw_elements.js";


export class Dropdown {

    // The server sends only the classifiers the website offers, each survey's in the order to list them.
    constructor(classifiers) {
        this._classifiers = classifiers;
        this._filtered_classifiers = [];
    }

    get filtered_classifiers() {
        return this._filtered_classifiers;
    }


    filter_classifiers_by_survey(survey_id) {
        this._filtered_classifiers = this._classifiers.filter(classifier => classifier.survey_id === survey_id);
    }


}


export function restart_dropdown(selected_element, options_container) {
    clear_selected(selected_element);
    clean_nodes_in_dom(options_container)
}

function clear_selected(selected_element) {
    selected_element.textContent = "";
    delete selected_element.dataset.value;
    delete selected_element.dataset.classifier;
}   

export function init_classifiers_dropdown(classifiers_dropdown, survey_id) {
    configure_dropdown_by_survey(classifiers_dropdown, survey_id);
    dropdown_classifiers_options_configure(classifiers_dropdown.filtered_classifiers);
}


function configure_dropdown_by_survey(classifiers_dropdown, survey_id) {
    classifiers_dropdown.filter_classifiers_by_survey(survey_id);
}

function dropdown_classifiers_options_configure(classifiers) {
    let selected = document.getElementById("classifiers_selected");
    draw_empty_option(selected.dataset.placeholder, document.getElementById("classifiers_options"));
    draw_dropdown_options(classifiers, document.getElementById("classifiers_options"));
    
    add_classifiers_items_functionality(document.getElementById("classifiers_selected"), document.getElementById("classifiers_options"));
}

function add_classifiers_items_functionality(selected, options) {

    for (let item of options.querySelectorAll(".obj-custom-option")) {

        item.addEventListener('click', () => {

            withdraw_selected_item(options)
            switch_arrow_icon(document.getElementById("classifier_container"))

            restart_dropdown(document.getElementById("class_selected"), document.getElementById("classes_options"))

            if (item.dataset.empty) {
                clear_selected(selected)
                return
            }

            change_selected_item(item) 
            selected.textContent = item.textContent;
            selected.setAttribute("data-classifier", item.getAttribute("data-classifier"));
            
            dropdown_classes_configure(item.getAttribute("data-classes"))

        })
    }


}


function dropdown_classes_configure(classes) {
    clean_nodes_in_dom(document.getElementById("classes_options"))
    draw_empty_option(document.getElementById("class_selected").dataset.placeholder, document.getElementById("classes_options"))
    draw_classes_options(classes.split(","))
    add_class_items_functionality(document.getElementById("classes_options"))
}


function add_class_items_functionality(options) {

    let selected = document.getElementById("class_selected")

    for (let item of options.querySelectorAll(".obj-custom-option")) {

        item.addEventListener('click', () => { 
            withdraw_selected_item(options)
            switch_arrow_icon(document.getElementById("class_container"))

            if (item.dataset.empty) {
                clear_selected(selected)
                return
            }

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
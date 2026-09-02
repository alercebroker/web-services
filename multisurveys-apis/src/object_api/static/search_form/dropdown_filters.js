import { draw_dropdown_options } from "../draw_elements.js";
import { clean_nodes_in_dom } from "../ui_helpers.js";
import { add_classifiers_items_functionality } from "./dinamic_select.js";


export class Dropdown {

    constructor(classifiers) {
        this._classifiers = classifiers;
        this._filtered_classifiers = [];
        this._priorities_by_survey = {}
    }

    get priorities_by_survey() {
        return this._priorities_by_survey;
    }

    get filtered_classifiers() {
        return this._filtered_classifiers;
    }


    set priorities_by_survey(survey_id) {
        if (survey_id === "ztf") {
            this._priorities_by_survey = {
                5: 0,
                4: 1,
                2: 2,
            };
        }
        else if (survey_id === "lsst") {
            this._priorities_by_survey = {
                3: 0,
                1: 1,
            };
        } else {
            this._priorities_by_survey = {};
        }

    }


    filter_classifiers_by_survey(survey_id) {
        this._filtered_classifiers = this._classifiers.filter(classifier => classifier.survey_id === survey_id);
    }

    order_by_priority(empty_array) {
        this._filtered_classifiers.forEach(classifier => {
            if (classifier.classifier_id in this._priorities_by_survey) {
                let index = this._priorities_by_survey[classifier.classifier_id];
                empty_array[index] = classifier;
            }
        });

        this._filtered_classifiers = [...empty_array.flat()]
    }


}


export function restart_dropdown(selected_element, options_container) {
    selected_element.textContent = selected_element.dataset.placeholder;
    selected_element.dataset.value = "";
    clean_nodes_in_dom(options_container)
}   

export function init_classifiers_dropdown(classifiers_dropdown, survey_id) {
    configure_dropdown_by_survey(classifiers_dropdown, survey_id);
    dropdown_classifiers_options_configure(classifiers_dropdown.filtered_classifiers);
}


function configure_dropdown_by_survey(classifiers_dropdown, survey_id) {
    classifiers_dropdown.priorities_by_survey = survey_id;
    classifiers_dropdown.filter_classifiers_by_survey(survey_id);
    classifiers_dropdown.order_by_priority(Array(8));
}

function dropdown_classifiers_options_configure(classifiers) {
    draw_dropdown_options(classifiers, document.getElementById("classifiers_options"));
    
    add_classifiers_items_functionality(document.getElementById("classifiers_selected"), document.getElementById("classifiers_options"));
}
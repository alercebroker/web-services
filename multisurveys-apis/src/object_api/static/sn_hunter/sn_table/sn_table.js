import { Paginator } from "./paginator.js";
import { draw_paginations_buttons, load_table_body } from "./table_tools.js";


export function init() {
    let raw = document.getElementById('sn_hunter_main_table');
    let data = JSON.parse(raw.dataset.sn);

    let previous_button = document.getElementById('prev_btn_sn');
    let next_button = document.getElementById('next_btn_sn');
    let paginator = new Paginator(data, 1);


    previous_button.addEventListener('click', () => {
        if (paginator.previous_page()) {
            render(paginator)
        }
    });

    next_button.addEventListener('click', () => {
        if (paginator.next_page()) {
            render(paginator)
        }
    });

    render(paginator)

}

function render(paginator) {
    load_table_body(paginator.page_data);
    draw_paginations_buttons(paginator)
}

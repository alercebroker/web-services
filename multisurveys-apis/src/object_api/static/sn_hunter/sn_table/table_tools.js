import { jdToDate } from "../../../libraries/AstroDates/AstroDates.js";
import { createIcon, default_icons_order, change_icon_order, draw_paginations_buttons } from '../draw_sn_tools.js';


export function render(paginator) {
    load_table_header(paginator);
    load_table_body(paginator.page_data);
    draw_paginations_buttons(paginator)
}


function load_table_header(paginator) {
    let table_head = document.querySelector('#sn_hunter_main_table thead');
    let header_data = paginator.header_data
    let tr = document.createElement('tr');
    
    header_data.forEach((item) => {
        let th = document.createElement('th');
        let text_container = document.createElement('div');
        
        config_th_element_default(text_container, item);
        add_listeners_th_element(text_container, paginator)

        th.appendChild(text_container);
        tr.appendChild(th);
    });
    
    clear_table_element(table_head);
    table_head.appendChild(tr);
}

function config_th_element_default(element, item) {
    element.dataset.attribute = item;
    element.dataset.ascendent = 'true';
    element.classList.add('th-table-style');
    element.innerHTML = get_header_text(item);
    element.appendChild(createIcon('unfoldMoreLess', { size: 16, color: '#1f1f1f' }));
}

export function get_header_text(item) {
    if (item === 'probability') {
        return 'Score';
    } else if (item === 'n_det') {
        return '#Obs';
    } else if (item === 'firstmjd') {
        return 'Discovery Date';
    }
    
    return item;
}

function add_listeners_th_element(element, paginator) {
    element.addEventListener('click', () => {
        let is_ascendent = element.dataset.ascendent === 'true';
        let attribute = element.dataset.attribute;
        let ordered_data = order_data_by_attribute(paginator._data, attribute, is_ascendent);

        paginator._data = ordered_data;
        default_icons_order(element)
        change_icon_order(element, is_ascendent);
        change_order_attribute(element, is_ascendent);
       
        load_table_body(paginator.page_data);
    });
}

function load_table_body(data) {
    let table_body = document.querySelector('#sn_hunter_main_table tbody');

    clear_table_element(table_body);

    data.forEach((row) => {
        let tr = document.createElement('tr');
        let discovery_date = jdToDate(row.firstmjd)

        tr.innerHTML = `
            <td class="padding-table-sn tw-border tw-border-[#dee2e6]">${row.oid}</td>
            <td class="padding-table-sn tw-border tw-border-[#dee2e6]">${get_discovery_date_text(discovery_date)}</td>
            <td class="padding-table-sn tw-border tw-border-[#dee2e6]">${row.probability.toFixed(3)}</td>
            <td class="padding-table-sn tw-border tw-border-[#dee2e6]">${row.n_det}</td>
            <td class="padding-table-sn tw-border tw-border-[#dee2e6]"></td>
        `;

        table_body.appendChild(tr);
    });
}

function clear_table_element(element) {
    element.innerHTML = '';
}

function get_discovery_date_text(date) {
    let day_str = pad(date.getUTCDate(), 2)
    let month_str = pad(date.getUTCMonth() + 1, 2)
    let year_str = date.getUTCFullYear()
    let hours_str = pad(date.getUTCHours(), 2)
    let minutes_str = pad(date.getUTCMinutes(), 2)
    let seconds_str = pad(date.getUTCSeconds(), 2)

    return `${day_str}/${month_str}/${year_str} ${hours_str}:${minutes_str}:${seconds_str} UTC`
}

function pad(str, max) {
  str = str.toString();
  return str.length < max ? pad('0' + str, max) : str;
}

export function order_data_by_attribute(data, attribute, is_ascendent) {
    let order_data = data.toSorted((a, b) => {
        if (is_ascendent) {
            return a[attribute] - b[attribute];
        } else {
            return b[attribute] - a[attribute];
        }
    });

    return order_data
}

export function change_order_attribute(element, is_ascendent) {
    element.dataset.ascendent = (!is_ascendent).toString();
}

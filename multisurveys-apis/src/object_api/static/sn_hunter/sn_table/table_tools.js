import { jdToDate } from "../../../libraries/AstroDates/AstroDates.js";


export function load_table_body(data) {
    let table_body = document.querySelector('#sn_hunter_main_table tbody');

    clear_table_body(table_body);

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

function clear_table_body(element) {
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

export function draw_paginations_buttons(paginator) {
    let page_container = document.getElementById('page_container')
    let pages_to_displays = pages_to_draw(paginator._current_page, paginator.total_pages)


    clean_pages_container(page_container)

    pages_to_displays.forEach((page) => {
        let new_button = build_button_sn_table(page, paginator)

        page_container.appendChild(new_button)
    })
}

function clean_pages_container(element) {
    element.innerHTML = ''
}

function pages_to_draw(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  if (current <= 3) return [1, 2, 3, 4, "...", total];
  if (current >= total - 2) return [1, "...", total-3, total-2, total-1, total];
  return [1, "...", current - 1, current, current + 1, "...", total];
}

function build_button_sn_table(index, paginator) {
    let button =  document.createElement('span')

    if (index === '...'){
        button.innerHTML = '...'
        
        return button
    }

    if(index == paginator._current_page){
        button.classList.add('current-page-style')
    }
    
    if(index != paginator._current_page){
        button.classList.add('btn-page-hover')
    }

    button.classList.add('btn-page-style')
    button.id = 'page_' + (index)
    button.innerHTML = index


    button.addEventListener('click', (event) => {
        paginator.current_page = parseInt(event.target.innerHTML)

        render(paginator)
    })

    return button
}
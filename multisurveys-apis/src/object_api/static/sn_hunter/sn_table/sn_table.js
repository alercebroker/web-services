import { jdToDate, jdToGregorian } from "../../../libraries/AstroDates/AstroDates.js";

class Paginator {
    constructor(data, rows_per_page) {
        this.data = data;
        this.rows_per_page = rows_per_page;
        this._current_page = 1;
        this._total_pages = this.calculate_total_pages();
    }

    set current_page(page) {
        this._current_page = page
    }

    get page_data() {
        return this.data.slice(this.start_index(), this.end_index());
    }

    get total_pages() {
        return this._total_pages
    }

    calculate_total_pages() {
        return Math.ceil(this.data.length / this.rows_per_page);
    }

    start_index() {
        return (this._current_page - 1) * this.rows_per_page;
    }

    end_index() {
        return this.start_index() + this.rows_per_page;
    }

    is_valid_page(page) {
        return page >= 1 && page <= this._total_pages;
    }

    next_page() {
        if (this.is_valid_page(this._current_page + 1)) {
            this._current_page += 1;

            return true;
        }
    }

    previous_page() {
        if (this.is_valid_page(this._current_page - 1)) {
            this._current_page -= 1;

            return true;
        }
    }

}


export function init() {
    let raw = document.getElementById('sn_hunter_main_table');
    let data = JSON.parse(raw.dataset.sn);

    let previous_button = document.getElementById('prev_btn_sn');
    let next_button = document.getElementById('next_btn_sn');
    let paginator = new Paginator(data, 5);


    previous_button.addEventListener('click', () => {
        if (paginator.previous_page()) {
            load_table_body(paginator.page_data);
            
            unselect_current_page()
            select_next_page(paginator._current_page)
        }
    });

    next_button.addEventListener('click', () => {
        if (paginator.next_page()) {
            load_table_body(paginator.page_data);

            unselect_current_page()
            select_next_page(paginator._current_page)
        }
    });

    load_table_body(paginator.page_data);
    draw_paginations_buttons(paginator)

}


function load_table_body(data) {
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

function draw_paginations_buttons(paginator) {
    let page_container = document.getElementById('page_container')

    for(let i = 0; i < paginator.total_pages; i++) {
        let new_page_button =  build_button_sn_table(i, paginator)

        page_container.appendChild(new_page_button)
    }
}

function build_button_sn_table(index, paginator) {
    let button =  document.createElement('span')

    if(index == 0){
        button.classList.add('current-page-style')
    }
    
    if(index != 0){
        button.classList.add('btn-page-hover')
    }

    button.classList.add('btn-page-style')

    button.id = 'page_' + (index+1)
    button.innerHTML = index + 1

    button.addEventListener('click', (event) => {
        paginator.current_page = parseInt(event.target.innerHTML)

        load_table_body(paginator.page_data)
        unselect_current_page()
        select_next_page(paginator._current_page)
    })

    return button
}


function select_next_page(next_page) {
    let page = document.getElementById(`page_${next_page}`)

    page.classList.add('current-page-style')
    page.classList.remove('btn-page-hover')
}

function unselect_current_page() {
    let current_page = document.querySelector('span.current-page-style')

    current_page.classList.remove('current-page-style')
    current_page.classList.add('btn-page-hover')

}
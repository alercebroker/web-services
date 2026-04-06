import { jdToDate, jdToGregorian } from "../../../libraries/AstroDates/AstroDates.js";

class Paginator {
    constructor(data, rows_per_page) {
        this.data = data;
        this.rows_per_page = rows_per_page;
        this.current_page = 1;
        this.total_pages = this.calculate_total_pages();
    }

    get page_data() {
        return this.data.slice(this.start_index(), this.end_index());
    }

    calculate_total_pages() {
        return Math.ceil(this.data.length / this.rows_per_page);
    }

    start_index() {
        return (this.current_page - 1) * this.rows_per_page;
    }

    end_index() {
        return this.start_index() + this.rows_per_page;
    }

    is_valid_page(page) {
        return page >= 1 && page <= this.total_pages;
    }

    next_page() {
        if (this.is_valid_page(this.current_page + 1)) {
            this.current_page += 1;

            return true;
        }
    }

    previous_page() {
        if (this.is_valid_page(this.current_page - 1)) {
            this.current_page -= 1;

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

    console.log(paginator.page_data)

    previous_button.addEventListener('click', () => {
        if (paginator.previous_page()) {
            load_table_body(paginator.page_data);
            document.getElementById('current_page').textContent = paginator.current_page;
        }
    });

    next_button.addEventListener('click', () => {
        if (paginator.next_page()) {
            load_table_body(paginator.page_data);
            document.getElementById('current_page').textContent = paginator.current_page;
        }
    });

    load_table_body(paginator.page_data);
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
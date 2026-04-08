import { Paginator } from "./paginator.js";
import { render } from "./table_tools.js";


export function init() {
    let raw = document.getElementById('sn_hunter_main_table');
    let data = JSON.parse(raw.dataset.sn);

    let search_input = document.getElementById('sn_hunter_search_input');

    let previous_button = document.getElementById('prev_btn_sn');
    let next_button = document.getElementById('next_btn_sn');
    let rows_per_page = 5;
    let paginator = new Paginator(data, rows_per_page);


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

    search_input.addEventListener('input', (event) => {
        let search_value = event.target.value.toLowerCase();
        let filtered_data = data.filter((item) => {
            let oid = item.oid ? String(item.oid).toLowerCase() : '';
            return oid.includes(search_value);
        });

        paginator = new Paginator(filtered_data, rows_per_page);
        render(paginator);
    });

    render(paginator)

}

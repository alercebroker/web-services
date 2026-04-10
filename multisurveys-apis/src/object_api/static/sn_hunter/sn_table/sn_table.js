import { Paginator } from "./paginator.js";
import { render } from "./table_tools.js";
import { createIcon } from '../draw_sn_tools.js';
import { order_data_by_attribute, change_order_attribute } from './table_tools.js'

export function init() {
    let raw = document.getElementById('sn_hunter_main_table');
    let data = JSON.parse(raw.dataset.sn);
    let header_data = ['oid', 'firstmjd', 'probability', 'n_det', 'Reported'];
    // let dropdown = document.getElementById('sn_dropdown');
    let search_input = document.getElementById('sn_hunter_search_input');
    let previous_button = document.getElementById('prev_btn_sn');
    let next_button = document.getElementById('next_btn_sn');
    let rows_per_page = 5;
    let paginator = new Paginator(data, header_data, rows_per_page);


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

        paginator = new Paginator(filtered_data, header_data, rows_per_page);
        render(paginator);
    });
    
    // add_dropdown_functionality(dropdown)

    render(paginator)

}


function add_dropdown_functionality(element) {
    
    element.querySelectorAll('el-dropdown').forEach(dropdown => {
        let button = dropdown.querySelector('button');

        dropdown.querySelectorAll('el-menu span').forEach(item => {

            item.addEventListener('click', () => {
            // Actualiza el innerHTML del botón (componente padre) conservando el ícono SVG
            let is_ascendent = item.dataset.ascendent.toLowerCase() === 'true';
            let icon_order = is_ascendent ? createIcon('upArrow', { size: 16 }) : createIcon('downArrow', { size: 16 });
            let item_attribute = String(item.dataset.attribute);
            let order_data = order_data_by_attribute(data, item_attribute, is_ascendent);


            button.innerHTML = '';
            button.appendChild(document.createTextNode(item.textContent.trim() + ' '));
            button.appendChild(icon_order);

            paginator = new Paginator(order_data,['oid', 'firstmjd', 'probability', 'n_det', 'Reported'],rows_per_page);
            change_order_attribute(item, is_ascendent)
            render(paginator)

            // Cierra el menú luego de seleccionar
            let menu = dropdown.querySelector('el-menu');
            if (menu && typeof menu.hidePopover === 'function') {
                menu.hidePopover();
            }
            });
        });
    });
}
import { Paginator } from "./paginator.js";
import { render } from "./table_tools.js";


const Icons = {
    unfoldMoreLess: {
        viewBox: '0 -960 960 960',
        path: 'M480-120 300-300l58-58 122 122 122-122 58 58-180 180ZM358-598l-58-58 180-180 180 180-58 58-122-122-122 122Z'
    },
    downArrow: {
        viewBox: '0 -960 960 960',
        path: 'M480-345 240-585l56-56 184 183 184-183 56 56-240 240Z'
    },
    upArrow: {
        viewBox: '0 -960 960 960',
        path: 'm256-424-56-56 280-280 280 280-56 56-224-223-224 223Z'
    },
};

function createIcon(name, { size = 24, color = '#1f1f1f', className = '' } = {}) {
  let icon = Icons[name];
  if (!icon) throw new Error(`Ícono "${name}" no encontrado`);

  let svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', icon.viewBox);
  svg.setAttribute('width', `${size}px`);
  svg.setAttribute('height', `${size}px`);
  svg.setAttribute('fill', color);
  if (className) svg.setAttribute('class', className);

  let path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('d', icon.path);
  svg.appendChild(path);

  return svg;
}

function order_data_by_attribute(data, is_ascendent) {

    let order_data = data.toSorted((a, b) => {
        if (is_ascendent) {
            return a.oid - b.oid;
        } else {
            return b.oid - a.oid;
        }
    });

    return order_data
}

export function init() {
    let raw = document.getElementById('sn_hunter_main_table');
    let data = JSON.parse(raw.dataset.sn);

    let search_input = document.getElementById('sn_hunter_search_input');
    let order_by_id = document.getElementById('order_by_oid_element');

    order_by_id.addEventListener('click', () => {
        let is_ascendent = order_by_id.dataset.ascendent.toLowerCase() === 'true';
        let icon_order = is_ascendent ? createIcon('upArrow', { size: 16 }) : createIcon('downArrow', { size: 16 });
        let order_data = order_data_by_attribute(data, is_ascendent);

        
        order_by_id.lastChild.remove();
        order_by_id.appendChild(icon_order);
        order_by_id.dataset.ascendent = (!is_ascendent).toString();

        paginator = new Paginator(order_data, rows_per_page);
        render(paginator)
    })

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

import { render } from "./sn_table/table_tools.js";


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


export function createIcon(name, { size = 24, color = '#1f1f1f', className = '' } = {}) {
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

export function default_icons_order(element) {
    let table_th = document.querySelectorAll('#sn_hunter_main_table thead tr th div');

    table_th.forEach(div => {
        if(div.dataset.attribute != element.dataset.attribute){
            div.dataset.ascendent = 'true';
            div.lastElementChild.remove()
            div.appendChild(createIcon('unfoldMoreLess', { size: 16, color: '#1f1f1f' }));
        }
    })
}

export function change_icon_order(element, is_ascendent) {
    let icon_name = is_ascendent ? 'upArrow' : 'downArrow';
    let icon = createIcon(icon_name, { size: 16, color: '#1f1f1f' });

    element.lastElementChild.remove()
    element.appendChild(icon);
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

function clean_pages_container(element) {
    element.innerHTML = ''
}

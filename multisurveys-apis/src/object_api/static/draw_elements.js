
export function draw_span(text){
    let new_span = document.createElement("span")
    new_span.innerHTML = text
    new_span.classList.add("custom-span")
  
    return new_span
}


export function draw_close_tags(father_element, div_tag, oid, oids_arr){
    let newBtn = document.createElement("div")

    let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", "18");
    svg.setAttribute("height", "18");
    svg.setAttribute("viewBox", "0 -960 960 960");
    svg.classList.add("custom-close-svg-id");
    
    let path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", "m336-280 144-144 144 144 56-56-144-144 144-144-56-56-144 144-144-144-56 56 144 144-144 144 56 56ZM480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Z");
    
    svg.appendChild(path);
    newBtn.appendChild(svg);
    newBtn.classList.add("tw-inline-block")

    newBtn.addEventListener("click", () =>{
        let index = oids_arr.indexOf(oid)
        let erase_tag = div_tag

        //se modifica el arr original
        if(index != -1){
            oids_arr.splice(index, 1)
        }

        father_element.removeChild(erase_tag)
    }, { once: true});

    return newBtn
}


export function draw_oids_tags(oids_arr){
  let container = document.getElementById("oids_container")

  for(let oid of oids_arr){
    let newDiv = document.createElement("div")
    newDiv.id = oid
    newDiv.classList.add("custom-oid")

    let new_span = draw_span(oid)
    let new_btn = draw_close_tags(container, newDiv, oid, oids_arr)

    newDiv.appendChild(new_span)
    newDiv.appendChild(new_btn)
    container.appendChild(newDiv)
  }
  
  container.classList.remove("tw-hidden")
}


export function draw_arrow_order_table(order_mode){
  let svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.id = 'selected_order_table'
  svg.setAttribute("viewBox", "0 -960 960 960");
  svg.setAttribute("width", "20px");
  svg.setAttribute("height", "20px");
  svg.classList.add("tw-inline-block", "tw-fill-black", "dark:tw-fill-white", "tw-hidden")


  let path = document.createElementNS("http://www.w3.org/2000/svg", "path");

  if(order_mode == 'DESC'){
    path.setAttribute("d", "M480-240 240-480l56-56 144 144v-368h80v368l144-144 56 56-240 240Z");
  } else {
    path.setAttribute("d", "M440-240v-368L296-464l-56-56 240-240 240 240-56 56-144-144v368h-80Z");
  }

  svg.appendChild(path)

  return svg
}


export function draw_error_message(message){
  const new_Div = document.createElement('div')
  const new_content = document.createElement("span")
  const new_Btn = draw_close_button(new_Div)

  new_content.innerHTML = message
  new_content.classList.add("tw-inline-block", "tw-w-full")

  new_Div.appendChild(new_content)
  new_Div.appendChild(new_Btn)

  new_Div.classList.add('custom-error')

  return new_Div
}

export function draw_close_button(element){
  const btn = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
  btn.id = "error_message_btn"
  btn.classList.add("tw-cursor-pointer", "tw-inline-block")
  btn.setAttribute('height', '24px');
  btn.setAttribute('viewBox', '0 -960 960 960');
  btn.setAttribute('width', '30px');
  btn.setAttribute('fill', '#C62828');

  
  const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  path.setAttribute('d', 'm256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z')

  btn.appendChild(path);

  btn.addEventListener("click", () => {
      element.remove()
  }, { once: true })

  return btn
}
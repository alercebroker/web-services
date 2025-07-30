

export function handle_error(){
    document.addEventListener('htmx:responseError', evt =>{

        const xhr = evt.detail.xhr

        if(xhr.status == 422) {
          const form = evt.detail.elt
          const errors_parsed = JSON.parse(xhr.responseText)
          const errors = errors_parsed.detail

          for (const name of Object.keys(errors)) {
            const field = document.getElementById(name)

            const message = draw_error_message(errors[name])

            field.after(message)
          }
        }
    
      });
}


function draw_error_message(message){
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

function draw_close_button(element){
    const btn = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    btn.id = "error_message"
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
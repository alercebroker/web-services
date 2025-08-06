import {draw_error_message} from "./draw_elements.js";

export function handle_error(){
  document.addEventListener('htmx:responseError', evt =>{

    const xhr = evt.detail.xhr
    search_for_old_error_message("error_message_btn")
    
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

    if(xhr.status == 500){
      let field = document.getElementById("search_filters")
      let message = draw_error_message("Error 500: Internal Server Error")
      message.classList.add('custom-bg-error')
      console.log(message)
      field.after(message)
    }

  });
}


function search_for_old_error_message(id_error){
  if(document.getElementById(id_error)){
    document.getElementById(id_error).parentNode.remove()
  }
}
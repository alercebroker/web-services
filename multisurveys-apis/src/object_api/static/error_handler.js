import {draw_error_message} from "./draw_elements.js";

export function handle_error(){
  const form = document.getElementById("form-search")
  if (!form) return

  // The search button targets #objects_table (outside the form), so we listen
  // on document and filter by whether the triggering element is inside the form.
  document.addEventListener('htmx:responseError', evt => {
    if (!form.contains(evt.detail.elt)) return

    const xhr = evt.detail.xhr
    search_for_old_error_message("error_message_btn")

    if (xhr.status === 422) {
      const errors = parse_response(xhr).detail
      if (errors && typeof errors === "object") {
        for (const name of Object.keys(errors)) {
          const field = document.getElementById(name)
          if (field) {
            const message = draw_error_message(errors[name])
            field.after(message)
          }
        }
        return
      }
    }

    const detail = parse_detail(xhr)
    const field = document.getElementById("search_filters")
    const message = draw_error_message(detail)
    message.classList.add('custom-bg-error')
    field.after(message)
  });

  document.addEventListener('htmx:afterRequest', evt => {
    if (!form.contains(evt.detail.elt)) return
    if (evt.detail.successful) {
      search_for_old_error_message("error_message_btn")
    }
  });
}


function parse_response(xhr) {
  try {
    return JSON.parse(xhr.responseText)
  } catch {
    return {}
  }
}

function parse_detail(xhr) {
  const body = parse_response(xhr)
  const detail = body.detail || xhr.statusText || "Unexpected error"
  return "Error " + xhr.status + ": " + detail
}

function search_for_old_error_message(id_error){
  if(document.getElementById(id_error)){
    document.getElementById(id_error).parentNode.remove()
  }
}

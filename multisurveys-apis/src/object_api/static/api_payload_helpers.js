

function send_classes_data(){
    let value_selected = document.getElementById("classifier").dataset.classes;
    let jsonString = value_selected.replace(/'/g, '"');
    let classes_array = JSON.parse(jsonString);
    
    return { classifier_classes: classes_array }
  }
  
function send_pagination_data(calling_page = 1){
    return {
        page: calling_page,
        page_size: 20,
        count: false,
    }
}

function send_order_data(column_name, current_order_mode, next_page = false){
    let selected_order_column = document.getElementById("selected_order_table").parentNode.dataset.column
  
    next_page = Boolean(next_page)
  
    if(column_name != selected_order_column){
      return {
        order_by: column_name,
        order_mode: "DESC"
      }
    }
    
    if(next_page){
      return {
        order_by: column_name,
        order_mode: current_order_mode
      }
    }
  
    return {
      order_by: column_name,
      order_mode: current_order_mode == "DESC" ? "ASC" : "DESC"
    }
}

function clean_nulls_form(form_response){
    for (let key in form_response) {
      if (form_response[key] === null) {
        delete form_response[key];
      }
    }
  
    return form_response
}


function get_values_array_fields(fields){

    let response_array = []
    let has_any_value = false

    for(let field of fields){
      let value = document.getElementById(field).value
      if(value != ""){
        response_array.push(value)
        has_any_value = true
      } else {
        response_array.push(null)
      }
    }

    if(!has_any_value){
      return []
    }

    return response_array
}
  

export {
    send_classes_data, 
    send_pagination_data, 
    send_order_data, 
    clean_nulls_form,
    get_values_array_fields
}
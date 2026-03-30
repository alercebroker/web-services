import { format_oids, check_radio_consearch } from "../ui_helpers.js";


function send_form_Data() {
  let ndet_arr = get_values_array_fields(["min_detections", "max_detections"])
  let first_mjd_arr = get_values_array_fields(["min_mjd", "max_mjd"])
  let probability_value = parseFloat(document.getElementById("prob_range").value);
  let class_selected = document.getElementById("class")
  let classifier_selected = document.getElementById("classifier")
  let survey_id = document.getElementById('survey')
  let list_oids = format_oids(JSON.parse(document.getElementById("oids_container").dataset.oids_list))
  let [ra_consearch, dec_consearch] = check_radio_consearch(
    document.getElementById('ra_consearch').value,
    document.getElementById('dec_consearch').value
  )
  let radius_consearch = document.getElementById('radius_consearch').value

  let response = {
    oid: list_oids == '' ? null : list_oids,
    classifier: classifier_selected.dataset.classifier == "" ? null : classifier_selected.dataset.classifier,
    class_name: class_selected.dataset.value == "" ? null : class_selected.dataset.value,
    survey: survey_id.dataset.survey,
    probability: probability_value > 0 ? probability_value : null,
    n_det_min: ndet_arr.length > 0 && ndet_arr[0] !== null ? parseInt(ndet_arr[0]) : null,
    n_det_max: ndet_arr.length > 1 && ndet_arr[1] !== null ? parseInt(ndet_arr[1]) : null,
    firstmjd: first_mjd_arr.length > 0 ? first_mjd_arr : null,
    ra: !isNaN(parseFloat(ra_consearch)) ? ra_consearch : null,
    dec: !isNaN(parseFloat(dec_consearch)) ? dec_consearch : null,
    radius: !isNaN(parseFloat(radius_consearch)) ? radius_consearch : null,
  }

  response = clean_nulls_form(response)

  return response
}

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


function _check_is_empty(value){
  if(value == ''){
    return true
  }

  return false
}

function _check_max_arr_position(index, response_array){
  if (index == 1 && response_array.length == 0 ){
    return true
  }

  return false
}

function get_values_array_fields(fields){
  let response_array = []

  for(let [index, field] of fields.entries()){
    let field_value = document.getElementById(field).value

    if(_check_max_arr_position(index, response_array) && !_check_is_empty(field_value)){
      response_array.push(0)
    }

    if(!_check_is_empty(field_value)){
      response_array.push(field_value)
    }
  }

  
  return response_array
}

export {
  send_classes_data, 
  send_pagination_data, 
  send_order_data, 
  clean_nulls_form,
  get_values_array_fields,
  send_form_Data
}
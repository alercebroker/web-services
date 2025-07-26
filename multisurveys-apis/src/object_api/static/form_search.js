import { jdToDate, gregorianToJd } from "./AstroDates.js"
import { getUTCDate, extractDate, extractTime, convertToDate, formatDate} from "./time.js"
import { handle_error } from "./error_handler.js";
import {draw_oids_tags} from "./draw_elements.js";
import { display, split_oids, format_oids, survey_emphasize }  from "./ui_helpers.js";

let oids_arr = []

export function init(){
    
  let info = JSON.parse(document.getElementById("form-data").text);
  let item_name = ""
  let minDate = ""
  let minDatetime = ""
  let dateUTC = ""

  let ztf_btn = document.getElementById("ztf_btn")
  let lsst_btn = document.getElementById("lsst_btn")

  let general_filters = document.getElementById("general_filters")
  let discovery_date_filters = document.getElementById("discovery_date_filters")
  let conesearch_filters = document.getElementById("conesearch_filters")

  let clear_oids = document.getElementById("clear_oids_btn")
  let oids_container = document.getElementById("oids_container")
  let prob_range = document.getElementById("prob_range")
  let min_detections = document.getElementById("min_detections")
  let max_detections = document.getElementById("max_detections")
  let input_ids = document.getElementById("objectIds")

  let min_mjd = document.getElementById("min_mjd")
  let min_date_time_text = document.getElementById("min_date_time_text")
  let date_min = document.getElementById("date_min")
  let time_min = document.getElementById("time_min")
  let save_date = document.getElementById("save_date")
  
  let max_mjd = document.getElementById("max_mjd")
  let max_date_time_text = document.getElementById("max_date_time_text")
  let date_max = document.getElementById("date_max")
  let time_max = document.getElementById("time_max")
  let save_date_max = document.getElementById("save_date_max")

  // se seleccionan todos los dropdowns
  for (const dropdown of document.querySelectorAll(".obj-select-wrapper")) {
    dropdown.addEventListener('click', function() {
      this.querySelector('.obj-select').classList.toggle('open');
    })
  }

  // Se incorporan funcionalidad a las opciones de los dropdowns
  for(const option of document.querySelectorAll(".obj-custom-option")){
    option.addEventListener('click', () => {
        if(!option.classList.contains('obj-selected')){
            
          option.parentNode.querySelector('.obj-custom-option.obj-selected').classList.remove('obj-selected');
          
          option.classList.add('obj-selected');
          
          option.closest('.obj-select').querySelector('.obj-select__trigger span').textContent = option.textContent;

          option.closest('.obj-select').querySelector('.obj-select__trigger span').setAttribute("data-classes",  option.getAttribute("data-classes"));
          option.closest('.obj-select').querySelector('.obj-select__trigger span').setAttribute("data-classifier",  option.getAttribute("data-classifier"));
          option.closest('.obj-select').querySelector('.obj-select__trigger span').setAttribute("data-version",  option.getAttribute("data-version"));



          if(option.closest('.obj-select').querySelector('.obj-select__trigger span').id == "classifier"){
            document.getElementById("classifier").dispatchEvent(new Event("change"))
          }
        }
    })
  }

  // handle errors
  handle_error()


  // clicks events
  general_filters.addEventListener("click", () =>{
    item_name = general_filters.id + "_container"
    display(item_name)
  })

  discovery_date_filters.addEventListener("click", () =>{
    item_name = discovery_date_filters.id + "_container"
    display(item_name)
  })

  conesearch_filters.addEventListener("click", () =>{
    item_name = conesearch_filters.id + "_container"
    display(item_name)
  })

  min_date_time_text.addEventListener("click", () => {
    item_name = min_date_time_text.id + "_container"
    display(item_name)
  })

  max_date_time_text.addEventListener("click", () => {
    item_name = max_date_time_text.id + "_container"
    display(item_name)
  })

  save_date.addEventListener("click", () => {
    display("min_date_time_text_container")
  })

  save_date_max.addEventListener("click", () => {
    display("max_date_time_text_container")
  })

  clear_oids.addEventListener("click", () =>{
    oids_arr = []

    while(oids_container.firstChild){
      oids_container.removeChild(oids_container.firstChild)
    }

    clear_oids.classList.add("tw-hidden")
  })

  date_min.addEventListener("click", () => {
    date_min.showPicker()
  })

  time_min.addEventListener("click", () => {
    time_min.showPicker()
  })

  date_max.addEventListener("click", () => {
    date_max.showPicker()
  })

  time_max.addEventListener("click", () => {
    time_max.showPicker()
  })

  ztf_btn.addEventListener("click", () => {
    survey_emphasize(ztf_btn)
  })

  lsst_btn.addEventListener("click", () => {
    survey_emphasize(lsst_btn)
  })

  // inputs events
  prob_range.addEventListener("input", () => {
    document.getElementById("prob_number").innerHTML = prob_range.value
  })

  min_mjd.addEventListener("input", () => {
    minDate = jdToDate(min_mjd.value)
    min_date_time_text.innerHTML = formatDate(minDate)

    minDatetime = getUTCDate(minDate)
    date_min.value = extractDate(minDatetime)
    time_min.value = extractTime(minDatetime)
  })

  max_mjd.addEventListener("input", () => {
    let maxDate = jdToDate(max_mjd.value)
    max_date_time_text.innerHTML = formatDate(maxDate)

    let maxDatetime = getUTCDate(maxDate)
    date_max.value = extractDate(maxDatetime)
    time_max.value = extractTime(maxDatetime)
  })


  // changes events
  input_ids.addEventListener("change", () => {
    oids_arr = split_oids(input_ids.value)
    draw_oids_tags(oids_arr)
    clear_oids.classList.remove("tw-hidden")

    input_ids.value = ""
  })

  min_detections.addEventListener("change", () =>{
    max_detections.removeAttribute("disabled")
  })

  date_min.addEventListener("change", () => {
    dateUTC = convertToDate(date_min.value, time_min.value)
    dateUTC = gregorianToJd(dateUTC)

    min_mjd.value = dateUTC
    min_mjd.dispatchEvent(new Event('input'))
  })

  time_min.addEventListener("change", () => {
    dateUTC = convertToDate(date_min.value, time_min.value)
    dateUTC = gregorianToJd(dateUTC)

    min_mjd.value = dateUTC
    min_mjd.dispatchEvent(new Event('input'))
  })

  date_max.addEventListener("change", () => {
    dateUTC = convertToDate(date_max.value, time_max.value)
    dateUTC = gregorianToJd(dateUTC)

    max_mjd.value = dateUTC
    max_mjd.dispatchEvent(new Event('input'))
  })

  time_max.addEventListener("change", () => {
    dateUTC = convertToDate(date_max.value, time_max.value)
    dateUTC = gregorianToJd(dateUTC)

    max_mjd.value = dateUTC
    max_mjd.dispatchEvent(new Event('input'))
  })


  /**funciones publicas para usarlas con HTMX */
  window.send_classes_data = send_classes_data
  window.send_form_Data = send_form_Data
  window.send_pagination_data = send_pagination_data
}


export function elementReady(selector) {
    return new Promise((resolve, reject) => {
      const el = document.querySelector(selector);
      if (el) {
        resolve(el);
      }
  
      new MutationObserver((mutationRecords, observer) => {
        Array.from(document.querySelectorAll(selector)).forEach(element => {
          resolve(element);
          observer.disconnect();
        });
      })
      .observe(document.documentElement, {
        childList: true,
        subtree: true
      });
    });
}


function send_classes_data(){
  let value_selected = document.getElementById("classifier").dataset.classes;
  let jsonString = value_selected.replace(/'/g, '"');
  let classes_array = JSON.parse(jsonString);
  
  return { classifier_classes: classes_array }
}

function send_pagination_data(calling_page = 1){
  if(!document.getElementById("pagination")){
    return {
      page: 1,
      page_size: 20,
      count: false,
    }
  }

  return {
    page: calling_page,
    page_size: 20,
    count: false,
  }
}


function send_form_Data(){
  let ndet_arr = []
  let first_mjd_arr = []
  let detections = ["min_detections", "max_detections"]
  let first_mjd = ["min_mjd", "max_mjd"]
  let probability_value = parseFloat(document.getElementById("prob_range").value);
  let class_selected = document.getElementById("class").getAttribute("data-value")
  let classifier_selected = document.getElementById("classifier")
  let survey_id = document.getElementById('survey')
  let list_oids = format_oids(oids_arr)

  for(let detection of detections){
    if(document.getElementById(detection).value != ""){
      ndet_arr.push(document.getElementById(detection).value)
    }
  }

  for(let mjd of first_mjd){
    if(document.getElementById(mjd).value != ""){
      first_mjd_arr.push(document.getElementById(mjd).value)
    }
  }


  let response = {
    oid: list_oids,
    classifier: classifier_selected.dataset.classifier,
    class_name: class_selected,
    survey: survey_id.dataset.survey,
    probability: probability_value > 0 ? probability_value : null,
    ndet: ndet_arr.length > 0 ? ndet_arr : null,
    firstmjd: first_mjd_arr.length > 0 ? first_mjd_arr : null,
  }

  for (let key in response) {
    if (response[key] === null) {
      delete response[key];
    }
  }
  
  console.log(response)

  return response
}
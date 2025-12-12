import { jdToDate, gregorianToJd, raDectoHMS, HMStoRa, DMStoDec} from "./AstroDates.js"
import { getUTCDate, extractDate, extractTime, convertToDate, formatDate} from "./time.js"
import { handle_error } from "./error_handler.js";
import {draw_oids_tags} from "./draw_elements.js";
import { display, highlight_text, split_oids, format_oids, survey_emphasize, check_radio_consearch, switch_arrow_icon }  from "./ui_helpers.js";
import {get_sesame_object} from "./sesame.js"
import { send_classes_data, send_pagination_data, send_order_data, clean_nulls_form, get_values_array_fields } from "./api_payload_helpers.js"

let oids_arr = []

export function init(){
    
  let item_name = ""
  let minDate = ""
  let minDatetime = ""
  let dateUTC = ""

  let ztf_btn = document.getElementById("ztf_btn")
  let lsst_btn = document.getElementById("lsst_btn")

  let general_filters = document.getElementById("general_filters")
  let discovery_date_filters = document.getElementById("discovery_date_filters")
  let conesearch_filters = document.getElementById("conesearch_filters")

  // let classifiers_list = document.getElementById("classifiers_list")
  // let classifiers_options = document.getElementById("classifiers_options")
  // let classes_list = document.getElementById("classes_list")
  // let classes_options = document.getElementById("classes_options")

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

  let resolve_btn = document.getElementById("resolve_btn")
  let radio_HMS = document.getElementById("HMS/DMS" )
  let radio_degress = document.getElementById("degrees")
  let clear_btn_form = document.getElementById("clear_form")

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

          if(!option.closest('.obj-select').querySelector('.obj-select__trigger span').classList.contains('dark:tw-text-[#EEEEEE]')){
            option.closest('.obj-select').querySelector('.obj-select__trigger span').classList.add('dark:tw-text-[#EEEEEE]')
          }


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
    switch_arrow_icon(general_filters)
    highlight_text(general_filters)
    display(item_name)
  })
  
  discovery_date_filters.addEventListener("click", () =>{
    item_name = discovery_date_filters.id + "_container"
    switch_arrow_icon(discovery_date_filters)
    highlight_text(discovery_date_filters)
    display(item_name)
  })
  
  conesearch_filters.addEventListener("click", () =>{
    item_name = conesearch_filters.id + "_container"
    switch_arrow_icon(conesearch_filters)
    highlight_text(conesearch_filters)
    display(item_name)
  })

  classifiers_list.addEventListener("click", () =>{
    item_name = classifiers_list.id + "_container"
    switch_arrow_icon(classifiers_list)
    highlight_text(classifiers_list)
  })

  classifiers_options.addEventListener("click", () =>{
    item_name = classifiers_list.id + "_container"
    switch_arrow_icon(classifiers_list)
    highlight_text(classifiers_list)
  })

  classes_list.addEventListener("click", () =>{
    item_name = classes_list.id + "_container"
    switch_arrow_icon(classes_list)
    highlight_text(classes_list)
  })

  classes_options.addEventListener("click", () =>{
    item_name = classes_list.id + "_container"
    switch_arrow_icon(classes_list)
    highlight_text(classes_list)
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

  radio_HMS.addEventListener("click", () => {
    let [ra_hms, dec_dms] = raDectoHMS(document.getElementById("ra_consearch").value, document.getElementById("dec_consearch").value).split(" ")

    document.getElementById("ra_consearch").type = "text" 
    document.getElementById("ra_consearch").value = ra_hms

    document.getElementById("dec_consearch").type = "text"
    document.getElementById("dec_consearch").value = dec_dms
  })

  radio_degress.addEventListener("click", () => {
    let ra_degree = HMStoRa(document.getElementById("ra_consearch").value)
    let dec_degree = DMStoDec(document.getElementById("dec_consearch").value)

    document.getElementById("ra_consearch").type = "number" 
    document.getElementById("ra_consearch").value = ra_degree

    document.getElementById("dec_consearch").type = "number"
    document.getElementById("dec_consearch").value = dec_degree
  })

  resolve_btn.addEventListener("click", () => {
    get_sesame_object(document.getElementById("target_name").value)
  })

  clear_btn_form.addEventListener("click", () => {
    reset_values()
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
  window.send_order_data = send_order_data
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


function reset_values(){
  document.getElementById("clear_oids_btn").click()
}

function send_form_Data(){
  let ndet_arr = get_values_array_fields(["min_detections", "max_detections"])
  let first_mjd_arr = get_values_array_fields(["min_mjd", "max_mjd"])
  let probability_value = parseFloat(document.getElementById("prob_range").value);
  let class_selected = document.getElementById("class")
  let classifier_selected = document.getElementById("classifier")
  let survey_id = document.getElementById('survey')
  let list_oids = format_oids(oids_arr)
  let [ra_consearch, dec_consearch] = check_radio_consearch(
    document.getElementById('ra_consearch').value, 
    document.getElementById('dec_consearch').value
  )
  let radius_consearch = document.getElementById('radius_consearch').value

  let response = {
    oid: list_oids == '' ? null : list_oids,
    classifier: classifier_selected.dataset.classifier == "" ? null : classifier_selected.dataset.classifier,
    class_name: class_selected.dataset.value == "" ? null : class_selected.dataset.value ,
    survey: survey_id.dataset.survey,
    probability: probability_value > 0 ? probability_value : null,
    n_det: ndet_arr.length > 0 ? ndet_arr : null,
    firstmjd: first_mjd_arr.length > 0 ? first_mjd_arr : null,
    ra: !isNaN(parseFloat(ra_consearch)) ? ra_consearch : null,
    dec: !isNaN(parseFloat(dec_consearch)) ? dec_consearch : null,
    radius: !isNaN(parseFloat(radius_consearch)) ? radius_consearch: null,
  }

  response = clean_nulls_form(response)

  return response
}
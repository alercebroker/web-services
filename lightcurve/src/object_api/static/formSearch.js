import { jdToDate, gregorianToJd } from "../core_static/utils/AstroDates.js"
import moment from 'https://cdn.skypack.dev/moment'

let oids_arr = []

export function init(){
    
  let info = JSON.parse(document.getElementById("form-data").text);
  let item_name = ""
  let mjd_jd = 0
  let minDate = ""
  let minDatetime = ""
  let dateUTC = ""


  let custom_select = document.querySelector(".select-wrapper")
  let initial_value = document.querySelector('.custom-option.selected').getAttribute("data-value")
  let general_filters = document.getElementById("general_filters")
  let discovery_date_filters = document.getElementById("discovery_date_filters")
  let conesearch_filters = document.getElementById("conesearch_filters")
  let prob_range = document.getElementById("prob_range")
  let min_detections = document.getElementById("min_detections")
  let max_detections = document.getElementById("max_detections")
  let input_ids = document.getElementById("objectId")
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


  for (const dropdown of document.querySelectorAll(".select-wrapper")) {
    dropdown.addEventListener('click', function() {
        this.querySelector('.select').classList.toggle('open');
    })
  }


  for(const option of document.querySelectorAll(".custom-option")){
    option.addEventListener('click', () => {
        if(!option.classList.contains('selected')){
            option.parentNode.querySelector('.custom-option.selected').classList.remove('selected');
            option.classList.add('selected');
            option.closest('.select').querySelector('.select__trigger span').textContent = option.textContent;
            option.closest('.select').querySelector('.select__trigger span').setAttribute("data-value",  option.getAttribute("data-value"));

            if(option.closest('.select').querySelector('.select__trigger span').id == "classifier"){
              document.getElementById("classifier").dispatchEvent(new Event("change"))
            }
        }
    })
}

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
    dateUTC = convertToDate(date_min.value, time_min.value)
    dateUTC = gregorianToJd(dateUTC)

    min_mjd.value = dateUTC
    min_mjd.dispatchEvent(new Event('input'))

    display("min_date_time_text_container")
  })

  save_date_max.addEventListener("click", () => {
    dateUTC = convertToDate(date_max.value, time_max.value)
    dateUTC = gregorianToJd(dateUTC)

    max_mjd.value = dateUTC
    max_mjd.dispatchEvent(new Event('input'))

    display("max_date_time_text_container")
  })

  prob_range.addEventListener("input", () => {
    document.getElementById("prob_number").innerHTML = prob_range.value
  })

  min_mjd.addEventListener("input", () => {
    minDate = jdToDate(min_mjd.value)
    min_date_time_text.innerHTML = moment.utc(minDate).format()

    minDatetime = getUTCDate(minDate)
    date_min.value = extractDate(minDatetime)
    time_min.value = extractTime(minDatetime)
  })

  max_mjd.addEventListener("input", () => {
    let maxDate = jdToDate(max_mjd.value)
    max_date_time_text.innerHTML = moment.utc(maxDate).format()

    let maxDatetime = getUTCDate(maxDate)
    date_max.value = extractDate(maxDatetime)
    time_max.value = extractTime(maxDatetime)
  })

  input_ids.addEventListener("change", () => {
    oids_arr = splitOids(input_ids.value)

  })

  min_detections.addEventListener("change", () =>{
    max_detections.removeAttribute("disabled")
  })


  window.calculateClass = calculateClass
  window.searchParams = searchParams
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


function display(item){
    item = document.getElementById(item)
    if(item.classList.contains("tw-hidden")){
        item.classList.remove("tw-hidden")
    } else {
        item.classList.add("tw-hidden")
    }
}


function calculateClass(){
  let value_select = document.getElementById("classifier").getAttribute("data-value");
  
  console.log(value_select)
  value_select = value_select.replace(/'/g, '"');
  value_select = JSON.parse(value_select);
  
  
  return {
    classifier_name: value_select.classifier_name,
    classifier_version: value_select.classifier_version

  }
}

function splitOids(oids_values){
  return oids_values.split(/[,;]*\s|\s|\n/g)
}

function formatOids(listOfOids) {
  const reducer = (accumulator, current) =>
    accumulator.concat(current.split(/[,;]*\s|\s|\n/g))
  let oids = listOfOids.reduce(reducer, [])
  oids = oids.map((x) => x.trim())
  oids = Array.from(new Set(oids))
  return oids
}

function getUTCDate(date) {
  if (!date) return null
  const dateStr = date.toUTCString()
  return moment.utc(dateStr).toDate()
}

function extractDate(datetime) {
  if (!datetime) return null
  return moment.utc(datetime).format('YYYY-MM-DD')
}

function extractTime(datetime) {
  if (!datetime) return null
  return moment.utc(datetime).format('HH:mm')
}

function convertToDate(date, time) {
  let strDate = date + '-' + time
  if (date && !time) {
    strDate = date + '-' + '00:00'
  }
  if (!date) {
    return null
  }
  return moment.utc(strDate, 'YYYY-MM-DD-HH:mm').toDate()
}

function searchParams(){
  let classifier_select = calculateClass()
  let class_selected = document.getElementById("class").getAttribute("data-value")
  let ndet_arr = []
  let first_mjd_arr = []
  let detections = ["min_detections", "max_detections"]
  let first_mjd = ["min_mjd", "max_mjd"]
  let probValue = parseFloat(document.getElementById("prob_range").value);
  let list_oids = formatOids(oids_arr)

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
    classifier: classifier_select.classifier_name,
    class_name: class_selected,
    probability: probValue > 0 ? probValue : null,
    ndet: ndet_arr.length > 0 ? ndet_arr : null,
    firstmjd: first_mjd_arr.length > 0 ? first_mjd_arr : null,
    page: 1,
    page_size: 20,
    count: false,
  }

  for (let key in response) {
    if (response[key] === null) {
      delete response[key];
    }
  }
  


  return response

  // return {
  //   oid: "",
  //   classifier: classifier_select.classifier_name,
  //   classifier_version: classifier_select.classifier_version,
  //   class_name: document.getElementById("class").value,
  //   ranking: null,
  //   ndet: document.getElementById("detections_range").value,
  //   probability: document.getElementById("prob_range").value,
  //   firstmjd: null,
  //   lastmjd: null,
  //   dec: null,
  //   ra: null,
  //   radius: null,
  //   page: 1,
  //   page_size: 10,
  //   count: false,
  //   order_by: null,
  //   order_mode: null
  // }
}
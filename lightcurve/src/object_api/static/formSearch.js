import { jdToDate, gregorianToJd } from "../core_static/utils/AstroDates.js"
import { getUTCDate, extractDate, extractTime, convertToDate, formatDate} from "./time.js"

let oids_arr = []

export function init(){
    
  let info = JSON.parse(document.getElementById("form-data").text);
  let item_name = ""
  let minDate = ""
  let minDatetime = ""
  let dateUTC = ""

  let general_filters = document.getElementById("general_filters")
  let discovery_date_filters = document.getElementById("discovery_date_filters")
  let conesearch_filters = document.getElementById("conesearch_filters")

  let clear_oids = document.getElementById("clear_oids_btn")
  let oids_container = document.getElementById("oids_container")
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

  clear_oids.addEventListener("click", () =>{
    oids_arr = []

    while(oids_container.firstChild){
      oids_container.removeChild(oids_container.firstChild)
    }

    clear_oids.classList.add("tw-hidden")
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
    oids_arr = splitOids(input_ids.value)
    drawOidsTags()
    clear_oids.classList.remove("tw-hidden")

    input_ids.value = ""
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

function drawOidsTags(){
  let container = document.getElementById("oids_container")

  for(let oid of oids_arr){
    let newDiv = document.createElement("div")
    let newSpan = document.createElement("span")
    let newBtn = document.createElement("div")

    newDiv.id = oid
    newSpan.innerHTML = oid
    newBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 -960 960 960" width="18px" fill="#FFFFFF"><path d="m330-288 150-150 150 150 42-42-150-150 150-150-42-42-150 150-150-150-42 42 150 150-150 150 42 42ZM480-80q-82 0-155-31.5t-127.5-86Q143-252 111.5-325T80-480q0-83 31.5-156t86-127Q252-817 325-848.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 82-31.5 155T763-197.5q-54 54.5-127 86T480-80Z"/></svg>'

    newBtn.addEventListener("click", () =>{
      oids_arr = oids_arr.filter((element) => {
        if (element != newDiv.id){
          return element
        }
      })

      container.removeChild(newDiv)
    }, { once: true});


    newDiv.classList.add( "custom-oid")
    newSpan.classList.add("custom-span")
    newBtn.classList.add("custom-close-id")

    newDiv.appendChild(newSpan)
    newDiv.appendChild(newBtn)
    container.appendChild(newDiv)
  }
  
  container.classList.remove("tw-hidden")
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
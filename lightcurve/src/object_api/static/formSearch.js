
export function init(){
    
  let info = JSON.parse(document.getElementById("form-data").text);
  let item_name = ""

  let general_filters = document.getElementById("general_filters")
  let discovery_date_filters = document.getElementById("discovery_date_filters")
  let conesearch_filters = document.getElementById("conesearch_filters")
  let prob_range = document.getElementById("prob_range")
  let min_detections = document.getElementById("min_detections")
  let max_detections = document.getElementById("max_detections")

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


  prob_range.addEventListener("input", () => {
    document.getElementById("prob_number").innerHTML = prob_range.value
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
  let value_select = document.getElementById("classifier").value;
  
  value_select = value_select.replace(/'/g, '"');
  value_select = JSON.parse(value_select);
  
  
  return {
    classifier_name: value_select.classifier_name,
    classifier_version: value_select.classifier_version

  }
}


function searchParams(){
  let classifier_select = calculateClass()
  let ndet_arr = []
  let detections = ["min_detections", "max_detections"]
  let probValue = parseFloat(document.getElementById("prob_range").value);

  for(let detection of detections){
    if(document.getElementById(detection).value != ""){
      ndet_arr.push(document.getElementById(detection).value)
    }
  }


  let response = {
    classifier: classifier_select.classifier_name,
    class_name: document.getElementById("class").value,
    probability: probValue > 0 ? probValue : null,
    ndet: ndet_arr.length > 0 ? ndet_arr : null,
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
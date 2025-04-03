
export function init(){
    
  let info = JSON.parse(document.getElementById("form-data").text);
  let item_name = ""

  let general_filters = document.getElementById("general_filters")
  let discovery_date_filters = document.getElementById("discovery_date_filters")
  let conesearch_filters = document.getElementById("conesearch_filters")
  let prob_range = document.getElementById("prob_range")
  let detections_range = document.getElementById("detections_range")

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

  detections_range.addEventListener("input", () =>{
    document.getElementById("max_detections").value = detections_range.value
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

  let filter_args_object = {
    oid: "",
    classifier: classifier_select.classifier_name,
    classifier_version: classifier_select.classifier_version,
    class_name: document.getElementById("class").value,
    ranking: "",
    ndet: document.getElementById("detections_range").value,
    probability: document.getElementById("prob_range").value,
    firstmjd: "",
    lastmjd: "",
  }

  let conesearch_args_object = {
    dec: "",
    ra: "",
    radius: "",
  }

  let pagination_args_object = {
    page: 1,
    page_size: 20,
    count: false,
  }

  let order_args_object = {
    order_by: "",
    order_mode: ""
  }

  console.log(filter_args_object)
  return {
    filter_args: JSON.stringify(filter_args_object),
    conesearch_args: JSON.stringify(conesearch_args_object),
    pagination_args: JSON.stringify(pagination_args_object),
    order_args: JSON.stringify(order_args_object),
  }
}
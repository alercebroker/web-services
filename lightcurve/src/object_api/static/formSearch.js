
export function init(){
    let item_name = ""
    let general_filters = document.getElementById("general_filters")
    let discovery_date_filters = document.getElementById("discovery_date_filters")
    let conesearch_filters = document.getElementById("conesearch_filters")


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

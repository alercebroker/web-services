import { highlight_new_object } from "./ui_objects_selector.js";
import { prepare_params } from "./manage_url_params.js";


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

export function init(){
  window.prepare_params = prepare_params
  window.highlight_new_object = highlight_new_object
}
import { jdToDate, gregorianToJd, raDectoHMS, HMStoRa, DMStoDec } from "../../libraries/AstroDates/AstroDates.js"
import { handle_error } from "../error_handler.js";
import { draw_dropdown_options, draw_oids_tags, draw_warning_message } from "../draw_elements.js";
import { display, highlight_text, split_oids, set_oids_in_container, survey_emphasize, switch_arrow_icon, clean_oids_container, clean_nodes_in_dom } from "../ui_helpers.js";
import { get_sesame_object } from "./sesame.js"
import { send_classes_data, send_pagination_data, send_order_data, send_form_Data } from "./api_payload_helpers.js"
import { restore_survey, restore_object_id, restore_classifier, restore_class, restore_probability, restore_n_det, restore_mjd, restore_last_alert_date, restore_prob_lastmjd, restore_conesearch } from "./form_restore_functions.js";
import { Dropdown, restart_dropdown, init_classifiers_dropdown } from "./dropdown_config.js";


let currentStates = null

export function init() {

  if (currentStates) {
    const statesToRestore = currentStates
    setTimeout(() => {
      restore_states(statesToRestore)
    }, 100)
    currentStates = null
  }

  let classifiers_data = JSON.parse(document.getElementById("form-data").textContent);
  let Dropdown_classifiers = new Dropdown(classifiers_data.classifiers)


  let ztf_btn = document.getElementById("ztf_btn")
  let lsst_btn = document.getElementById("lsst_btn")

  let clear_oids = document.getElementById("clear_oids_btn")
  let oids_container = document.getElementById("oids_container")
  let prob_range = document.getElementById("prob_range")
  let input_ids = document.getElementById("objectIds")

  let resolve_btn = document.getElementById("resolve_btn")
  let radio_HMS = document.getElementById("HMS/DMS")
  let radio_degress = document.getElementById("degrees")
  let clear_btn_form = document.getElementById("clear_form")


  // clicks events
  setup_filters_toggles()
  setup_mjd_date_inputs()
  setup_combined_filters_notice()

  clear_oids.addEventListener("click", () => {
    clean_oids_container(oids_container)

    oids_container.dataset.oids_list = "[]"
    oids_container.classList.add("tw-hidden")
  })


  ztf_btn.addEventListener("click", () => {
    survey_emphasize(ztf_btn)
    restart_dropdown(document.getElementById("classifiers_selected"), document.getElementById("classifiers_options"))

    restart_dropdown(document.getElementById("class_selected"), document.getElementById("classes_options"))

    init_classifiers_dropdown(Dropdown_classifiers, "ztf")
  })

  lsst_btn.addEventListener("click", () => {
    survey_emphasize(lsst_btn)
    restart_dropdown(document.getElementById("classifiers_selected"), document.getElementById("classifiers_options"))

    restart_dropdown(document.getElementById("class_selected"), document.getElementById("classes_options"))

    init_classifiers_dropdown(Dropdown_classifiers, "lsst")
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

  // Elements to delete form, get states of conesearch and discovery dates and restore states
  clear_btn_form.addEventListener("htmx:beforeRequest", () => {
    currentStates = get_states()
    reset_values()
  })

  // inputs events
  prob_range.addEventListener("input", () => {
    document.getElementById("prob_number").innerHTML = prob_range.value
  })


  // changes events
  input_ids.addEventListener("change", () => {
    let oids_parsed = split_oids(input_ids.value)

    clean_oids_container(oids_container)
    set_oids_in_container(oids_parsed)
    draw_oids_tags()
    
    input_ids.value = ""
  })

  // handle errors
  handle_error()

  init_classifiers_dropdown(Dropdown_classifiers, document.getElementById("survey").dataset.survey)


  /**funciones publicas para usarlas con HTMX */
  window.send_classes_data = send_classes_data
  window.send_form_Data = send_form_Data
  window.send_pagination_data = send_pagination_data
  window.send_order_data = send_order_data
  window.switch_arrow_icon = switch_arrow_icon


  setTimeout(() => {
    restore_form_from_url()
  }, 200)

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


// Collapsible sections: clicking a header shows or hides its "<id>_container".
const SECTIONS = ["classification_filters", "object_filters", "discovery_date_filters", "last_alert_date_filters", "classifier_date_filters", "conesearch_filters"]

// Sections that start collapsed and stay open across CLEAR.
const SUBSECTIONS = ["discovery_date_filters", "last_alert_date_filters", "classifier_date_filters", "conesearch_filters"]


function setup_filters_toggles() {
  for (let id of SECTIONS) {
    let header = document.getElementById(id)

    header.addEventListener("click", () => {
      switch_arrow_icon(header)
      highlight_text(header)
      display(id + "_container")
    })
  }
}


const MJD_DATE_INPUTS = ["min_mjd", "max_mjd", "min_lastmjd", "max_lastmjd", "min_prob_lastmjd", "max_prob_lastmjd"]

// Each MJD box follows its DD/MM/YYYY HH:MM box and its calendar, all in UTC, to the minute.
function setup_mjd_date_inputs() {
  for (let id of MJD_DATE_INPUTS) {
    let mjd = document.getElementById(id)
    let text = document.getElementById(`${id}_date`)
    let picker = document.getElementById(`${id}_picker`)
    let calendar = document.getElementById(`${id}_calendar`)

    let show_date = () => {
      let date = mjd.value != '' ? to_minute(jdToDate(mjd.value)) : null
      let valid = date !== null && !isNaN(date.getTime())

      text.value = valid ? format_date_time(date) : ''
      picker.value = valid ? date.toISOString().slice(0, 16) : ''
    }

    // 6 decimals of MJD are below a tenth of a second, and drop the float noise of the conversion.
    let set_mjd = (date) => {
      mjd.value = date !== null ? Number(gregorianToJd(date).toFixed(6)) : ''
      show_date()
    }

    mjd.addEventListener("input", show_date)

    // An unreadable date puts back the one the MJD box holds.
    text.addEventListener("change", () => {
      if (text.value.trim() == '') {
        set_mjd(null)
        return
      }

      let date = parse_date_time(text.value)
      date !== null ? set_mjd(date) : show_date()
    })

    picker.addEventListener("change", () => {
      set_mjd(picker.value != '' ? new Date(picker.value + "Z") : null)
    })

    calendar.addEventListener("click", () => {
      picker.showPicker()
    })
  }
}


function to_minute(date) {
  return date === null ? null : new Date(Math.round(date.getTime() / 60000) * 60000)
}


function format_date_time(date) {
  let pad = (n) => String(n).padStart(2, '0')
  return `${pad(date.getUTCDate())}/${pad(date.getUTCMonth() + 1)}/${date.getUTCFullYear()} `
    + `${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`
}


// DD/MM/YYYY, optionally followed by HH:MM (00:00 when left out).
function parse_date_time(text) {
  let match = text.trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})(?:\s+(\d{1,2}):(\d{2}))?$/)
  if (match === null) return null

  let [day, month, year, hour, minute] = match.slice(1).map((n) => Number(n ?? 0))
  if (hour > 23 || minute > 59) return null

  let date = new Date(Date.UTC(year, month - 1, day, hour, minute))

  // Date.UTC rolls 31/02 over to March: such a date does not exist.
  if (date.getUTCDate() != day || date.getUTCMonth() != month - 1) return null

  return date
}


// Object properties and classification filters can each be fast alone but slow together, so warn when
// both are set. The notice shows each time they become combined, and goes away when they no longer are.
const COMBINED_FILTERS_NOTICE = "combined_filters_notice"
let combined_filters_were_set = false

function setup_combined_filters_notice() {
  combined_filters_were_set = false
  let form = document.getElementById("form-container")

  // Dropdowns update their selection on click, after the event: check once they have.
  for (let event of ["input", "change", "click"]) {
    form.addEventListener(event, () => setTimeout(update_combined_filters_notice, 0))
  }
}


function update_combined_filters_notice() {
  let filled = (ids) => ids.some((id) => document.getElementById(id).value != '')

  let object_filters = filled([
    "min_detections", "max_detections", "min_mjd", "max_mjd", "min_lastmjd", "max_lastmjd",
    "ra_consearch", "dec_consearch", "radius_consearch",
  ])
  let classification_filters = (
    Boolean(document.getElementById("classifiers_selected").dataset.classifier)
    || Boolean(document.getElementById("class_selected").dataset.value)
    || parseFloat(document.getElementById("prob_range").value) > 0
    || filled(["min_prob_lastmjd", "max_prob_lastmjd"])
  )
  let combined = object_filters && classification_filters
  let notice = document.getElementById(COMBINED_FILTERS_NOTICE)

  if (combined && !combined_filters_were_set && notice === null) {
    let message = draw_warning_message(
      "Object Properties combined with Classification filters can make the search slow. "
      + "To narrow a class by date, \"Last detection used by the classifier\" is much faster.",
      COMBINED_FILTERS_NOTICE
    )
    document.getElementById("search_filters").after(message)
  }

  if (!combined && notice !== null) {
    notice.remove()
  }

  combined_filters_were_set = combined
}


function reset_values() {
  window.history.pushState({}, document.title, "/")
}


// Reopen the sections that were open, through their header so the arrow and color follow.
function restore_states(currentStates) {
  SUBSECTIONS.forEach((id, i) => {
    if (currentStates[i]) {
      document.getElementById(id).click()
    }
  })
}


function get_states() {
  return SUBSECTIONS.map((id) => !document.getElementById(id + "_container").classList.contains('tw-hidden'))
}


function restore_form_from_url() {
  const urlParams = new URLSearchParams(window.location.search)

  restore_object_id(urlParams)

  restore_survey(urlParams)

  restore_classifier(urlParams)

  restore_class(urlParams)

  restore_probability(urlParams)

  restore_n_det(urlParams)

  restore_mjd(urlParams)

  restore_last_alert_date(urlParams)

  restore_prob_lastmjd(urlParams)

  restore_conesearch(urlParams)

  update_combined_filters_notice()
}


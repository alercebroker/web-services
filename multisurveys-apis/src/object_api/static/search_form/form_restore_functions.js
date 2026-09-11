import { draw_oids_tags } from "../draw_elements.js";
import { survey_emphasize, split_oids, set_oids_in_container } from "../ui_helpers.js";

function restore_survey(urlParams) {

  const survey = urlParams.get('survey')

  if (survey) {

    if (survey === 'ztf') {
      document.getElementById('ztf_btn').dispatchEvent(new Event('click'))
    } else if (survey === 'lsst') {
      document.getElementById('lsst_btn').dispatchEvent(new Event('click'))
    }
  }

}

function restore_object_id(urlParams) {
  let oids = urlParams.getAll('oid')

  if (oids.length === 1) {
    oids = split_oids(oids[0])
  }

  if (oids.length > 0) {
    set_oids_in_container(oids)
    draw_oids_tags(oids)
    document.getElementById("clear_oids_btn").classList.remove("tw-hidden")
  }

}

function restore_classifier(urlParams) {

  let classifier = urlParams.get('classifier')

  if (classifier) {
    let options = document.querySelectorAll('#classifiers_options .obj-custom-option')


    options.forEach((option) => {
      if (option.getAttribute('data-classifier') === classifier){
        option.click()
      }

    })
  }
}

function restore_class(urlParams) {

  let className = urlParams.get('class_name')
  if (className) {

    let options = document.querySelectorAll('#classes_options .obj-custom-option')

    options.forEach((option) => {
      if (option.getAttribute('data-value') === className){
        option.click()
      }
    })
  }
}

function restore_probability(urlParams) {

  const probability = urlParams.get('probability')

  if (probability) {
    const probRange = document.getElementById('prob_range')
    probRange.value = probability
    document.getElementById('prob_number').innerHTML = probability
  }

}

function restore_n_det(urlParams) {

  const nDetMin = urlParams.get('n_det_min')
  const nDetMax = urlParams.get('n_det_max')

  if (nDetMin) {
    document.getElementById('min_detections').value = nDetMin
  }
  if (nDetMax) {
    document.getElementById('max_detections').value = nDetMax
  }

}

function restore_mjd(urlParams) {
  let firstmjd = urlParams.getAll('firstmjd')
  let lastmjd = urlParams.getAll('lastmjd')

  if (firstmjd.length > 0) {
    document.getElementById('min_mjd').value = firstmjd
    document.getElementById('min_mjd').dispatchEvent(new Event('input'))
  }

  if (lastmjd.length > 0) {
    document.getElementById('max_mjd').value = lastmjd
    document.getElementById('max_mjd').dispatchEvent(new Event('input'))
  }

}

function restore_conesearch(urlParams) {

  const ra = urlParams.get('ra')
  const dec = urlParams.get('dec')
  const radius = urlParams.get('radius')

  if (ra) document.getElementById('ra_consearch').value = ra
  if (dec) document.getElementById('dec_consearch').value = dec
  if (radius) document.getElementById('radius_consearch').value = radius
}

export { restore_survey, restore_object_id, restore_classifier, restore_class, restore_probability, restore_n_det, restore_mjd, restore_conesearch }

import { draw_oids_tags } from "./draw_elements.js";
import { survey_emphasize } from "./ui_helpers.js";

function restore_survey(urlParams) {

  const survey = urlParams.get('survey')

  if (survey) {

    document.getElementById('survey').dataset.survey = survey

    if (survey === 'ztf') {
      survey_emphasize(document.getElementById('ztf_btn'))
    } else if (survey === 'lsst') {
      survey_emphasize(document.getElementById('lsst_btn'))
    }
  }

}

function restore_object_id(urlParams) {

  let oids = urlParams.getAll('oid')

  if (oids.length === 1) {
    oids = oids[0].split(",")
  }
  if (oids.length > 0) {

    draw_oids_tags(oids)
    document.getElementById("clear_oids_btn").classList.remove("tw-hidden")
  }

}

function restore_classifier(urlParams) {

  const classifier = urlParams.get('classifier')

  if (classifier) {
    const classifierElement = document.getElementById('classifier')

    const classifierOptions = document.querySelectorAll('#classifiers_options .obj-custom-option')
    classifierOptions.forEach(option => {
      if (option.dataset.classifier === classifier) {

        classifierElement.setAttribute('data-classifier', option.dataset.classifier)
        classifierElement.setAttribute('data-classes', option.dataset.classes)
        classifierElement.textContent = option.textContent.trim()

        document.querySelector('#classifiers_options .obj-custom-option.obj-selected')?.classList.remove('obj-selected')
        option.classList.add('obj-selected')

        classifierElement.dispatchEvent(new Event('change'))
      }
    })
  }
}

function restore_class(urlParams) {

  const className = urlParams.get('class_name')
  let classes_options = document.getElementById('classes_options')
  if (className) {
    classes_options.addEventListener('htmx:afterSwap', function handleClassesLoaded(event) {
      if (event.detail.target.id === 'classes_options') {
        const classOptions = document.querySelectorAll('#classes_options .obj-custom-option')
        const classElement = document.getElementById('class')

        classOptions.forEach(option => {
          if (option.dataset.value === className) {
            const previousSelected = document.querySelector('#classes_options .obj-custom-option.obj-selected')
            if (previousSelected) {
              previousSelected.classList.remove('obj-selected')
            }

            option.classList.add('obj-selected')

            if (classElement) {
              classElement.textContent = option.textContent.trim()
              classElement.setAttribute('data-value', option.dataset.value)
            }
          }
        })

        classes_options.removeEventListener('htmx:afterSwap', handleClassesLoaded)
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

  const firstmjds = urlParams.getAll('firstmjd')
  if (firstmjds.length > 0) {
    if (firstmjds[0]) {
      document.getElementById('min_mjd').value = firstmjds[0]
      document.getElementById('min_mjd').dispatchEvent(new Event('input'))
    }
    if (firstmjds[1]) {
      document.getElementById('max_mjd').value = firstmjds[1]
      document.getElementById('max_mjd').dispatchEvent(new Event('input'))
    }
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

import { raDectoHMS, HMStoRa, DMStoDec } from "./AstroDates.js"

function display(item){
    item = document.getElementById(item)
    if(item.classList.contains("tw-hidden")){
      item.classList.remove("tw-hidden")
    } else {
      item.classList.add("tw-hidden")
    }
}


function highlight_text(item){
  if(item.classList.contains("tw-text-[#1976d2]")){
    item.classList.remove("tw-text-[#1976d2]", "hover:tw-bg-[#1976d2]/20")
    item.classList.add("hover:tw-bg-[#b2b2b2]")

    darken_icon_color(item)
  } else {
    item.classList.remove("hover:tw-bg-[#b2b2b2]")
    item.classList.add("tw-text-[#1976d2]", "hover:tw-bg-[#1976d2]/20")
    
    highlight_icon_color(item)
  }
}


function darken_icon_color(item){
  let svg_items = item.querySelectorAll('svg')

  svg_items.forEach((element) => {
    element.classList.remove("tw-fill-[#1976d2]", "dark:tw-fill-[#1976d2]")

    element.classList.add("tw-fill-dark", "dark:tw-fill-white")
  })
}


function highlight_icon_color(item){
  let svg_items = item.querySelectorAll('svg')

  svg_items.forEach((element) => {
    element.classList.add("tw-fill-[#1976d2]", "dark:tw-fill-[#1976d2]")

    element.classList.remove("tw-fill-dark", "dark:tw-fill-white")
  })
}


function switch_arrow_icon(item){
  for(let child of item.children){
    if(child.getAttribute('name') == 'arrow_icon'){
      let direction = child.dataset.direction
      let path = child.querySelector('path')

      if(direction == 'down'){
        child.dataset.direction = 'up'
        path.setAttribute('d', "M480-528 296-344l-56-56 240-240 240 240-56 56-184-184Z")
      } else {
        child.dataset.direction = 'down'
        path.setAttribute('d', "M480-344 240-584l56-56 184 184 184-184 56 56-240 240Z")
      }
    }
  }
}


function survey_emphasize(btn){
  document.getElementById("survey").dataset.survey = btn.textContent
  document.querySelector('.obj-survey-selected').classList.remove('obj-survey-selected')
  btn.classList.add('obj-survey-selected')
  btn.classList.remove('obj-surveys-unselect')

  surveys_blur_items()
}

function surveys_blur_items(){
  let surveys_items = [...document.querySelectorAll('#survey span')]

  surveys_items.forEach((e) => {
    if(!e.classList.contains('obj-survey-selected') && !e.classList.contains('obj-surveys-unselect')){
      e.classList.add('obj-surveys-unselect')
    }
  })
}


function split_oids(oids_values){
  let regExp = /[,;]+\s*/;
  return oids_values.split(regExp).filter(oid => oid.length > 0);
}

function format_oids(listOfOids) {
  const reducer = (accumulator, current) =>
    accumulator.concat(current.split(/[,;]*\s|\s|\n/g))
  let oids = listOfOids.reduce(reducer, [])
  oids = oids.map((x) => x.trim())
  oids = Array.from(new Set(oids))
  return oids.toString()
}


function check_radio_consearch(ra_consearch, dec_consearch){
  if(!document.getElementById('degrees').checked && typeof(ra_consearch) === 'string' && typeof(dec_consearch) === 'string'){
    ra_consearch = HMStoRa(ra_consearch)
    dec_consearch = DMStoDec(dec_consearch)

  } else if(!document.getElementById('degrees').checked){
    [ra_consearch, dec_consearch] = raDectoHMS(ra_consearch, dec_consearch).split(" ")
  }

  return [ra_consearch, dec_consearch]
}

export {display, highlight_text, split_oids, format_oids, survey_emphasize, check_radio_consearch, switch_arrow_icon}
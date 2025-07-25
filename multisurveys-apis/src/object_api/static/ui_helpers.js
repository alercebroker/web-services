function display(item){
    item = document.getElementById(item)
    if(item.classList.contains("tw-hidden")){
      item.classList.remove("tw-hidden")
    } else {
      item.classList.add("tw-hidden")
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
  let regExp = /[,;]*\s/
  return oids_values.split(regExp)
}


function format_oids(listOfOids) {
  const reducer = (accumulator, current) =>
    accumulator.concat(current.split(/[,;]*\s|\s|\n/g))
  let oids = listOfOids.reduce(reducer, [])
  oids = oids.map((x) => x.trim())
  oids = Array.from(new Set(oids))
  return oids
}


export {display, split_oids, format_oids, survey_emphasize}
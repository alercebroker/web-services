import { customToolTip } from "./customToolTip.js"

let probability_data_aux

let data = {
    labels: [],
    datasets: [{
        label: 'Probabilities',
        data: [],
        fill: true,
        backgroundColor: 'rgba(255, 0, 54, 0.7)',
        borderColor: 'rgb(255, 0, 54)',
        pointBackgroundColor: 'rgb(255, 0, 54)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(255, 0, 54)',
    }]
};


let config = {
    type: 'radar',
    data: data,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        pointRadius: 5,
        elements: {
            line: {
                borderWidth: 1,
                fill: true,
            }
        },
        scales: {
            r: {
                backgroundColor: 'white',
                ticks: {
                    display: false,
                    stepSize: 0.33,
                },
                angleLines: {
                    color: '#000000'
                },
                grid: {
                    color: '#000000',
                },
                pointLabels: {
                    color: '#000000',
                    font: {
                        size: 14
                    }
                },
                beginAtZero: true,
                max: 1
            },
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                enabled: false,
                mode: 'dataset',
                position: 'nearest',
                external: customToolTip,
                /*titleFont: {
                    weight: 'bold'
                },
                displayColors: false,
                callbacks: {
                    title: function(){
                        return "Probabilities (score)"
                    },
                    label: function(context){
                        let tooltipText = [];
                        let length = context.dataset.data.length - 1
                        let data = context.dataset.data
                        let labels = context.chart.data.labels
                        
                        tooltipText.push(`${labels[0]}: ${data[0]}`)

                        for (let index = length; index >= 1; index--){
                            tooltipText.push(`${labels[index]}: ${data[index]}`)
                        }

                        return tooltipText
                    }
                }*/
            }
        },

    }
}

export function init(){
    let raw_data = JSON.parse(document.getElementById("probabilities-data").text);
    let raw_tax = raw_data.taxonomy_dict
    let raw_group_prob_dict = raw_data.group_prob_dict

    let ctx = document.getElementById('myChart');
    let custom_select = document.querySelector(".select-wrapper")
    let initial_value = document.querySelector('.custom-option.selected').getAttribute("data-value")

    reverseData(raw_tax)


    let mychart = new Chart(ctx, config);
    probability_data_aux = []

    updateMyChart(mychart, initial_value, raw_tax, raw_group_prob_dict)

    custom_select.addEventListener('click', () => {
        custom_select.querySelector('.select').classList.toggle('open');
    })

    for(const option of document.querySelectorAll(".custom-option")){
        option.addEventListener('click', () => {
            if(!option.classList.contains('selected')){
                option.parentNode.querySelector('.custom-option.selected').classList.remove('selected');
                option.classList.add('selected');
                option.closest('.select').querySelector('.select__trigger span').textContent = option.textContent;

                updateMyChart(mychart, option.getAttribute("data-value"), raw_tax, raw_group_prob_dict)
            }
        })
    }
}

function reverseData(raw_tax){
    let aux_arr = []

    Object.keys(raw_tax).forEach((key) => {
        aux_arr= raw_tax[key].classes.map((item, idx) => {
            if (idx == 0) {
                return item
            } else {
                return raw_tax[key].classes[raw_tax[key].classes.length - idx]
            }
        })
        raw_tax[key].classes = aux_arr
    })
}


function orderDataByTagNew(labels_tags, classifier_data){
    probability_data_aux.length = 0

    labels_tags.forEach((e) => {
        classifier_data.forEach((element) => {
            if(element.class_name == e){
                probability_data_aux.push(element.probability)
            }
        })
    })
}

function maxValue(classifier_data){
    let maxVal = Math.max.apply(Math, classifier_data.map((e) => e.probability))

    return maxVal
}

function getScale(max_value){
    return (max_value/3)
}

function updateMyChart(mychart, classifier_name, raw_tax, raw_group_prob_dict){
    let max_value
    let classes_arr = raw_tax[classifier_name].classes
    let classifier_data = Object.values(raw_group_prob_dict[classifier_name])[0]

    orderDataByTagNew(classes_arr, classifier_data)

    max_value = maxValue(classifier_data)

    removeDataChart(mychart)
    updateDataChart(mychart, classes_arr, max_value)

    isDark(mychart);
}

function removeDataChart(mychart){
    mychart.data.labels.length = 0;
    mychart.data.datasets.forEach((dataset) => {
        dataset.data.length = 0;

    });

    mychart.update();
}

function updateDataChart(mychart, labels, max_value){
    mychart.data.labels.push(...labels);
    mychart.data.datasets.forEach((dataset) => {
        dataset.data.push(...probability_data_aux);
    });

    mychart.config.options.scales.r.ticks.stepSize = getScale(max_value)
    mychart.config.options.scales.r.max = max_value

    mychart.update();
}

function isDark(mychart){
    if(document.getElementById("probabilities-app").classList.contains("tw-dark")){
        mychart.config.options.scales.r.backgroundColor = 'rgba(245, 245, 245, 0.2)'
        mychart.config.options.scales.r.angleLines.color = '#F5F5F5'
        mychart.config.options.scales.r.grid.color = '#F5F5F5'
        mychart.config.options.scales.r.pointLabels.color = '#F5F5F5'
        
        mychart.update();
    }
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
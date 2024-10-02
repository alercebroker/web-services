let probability_data_aux
let mychart

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
                    color: '#000000'
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
                enabled: true,
                mode: 'dataset',
                position: 'nearest',
                callbacks: {
                    title: function(){
                        return "Probability"
                    },
                    label: function(context){
                        let tooltipslabels = []
                        let label = ""
                        label = context.label + ": " + context.parsed.r
                        tooltipslabels.push(label)
                        return tooltipslabels
                    }
                }
            }
        },
    }
}

export function init(){
    let raw_data = JSON.parse(document.getElementById("probabilities-data").text);
    let raw_tax = raw_data.taxonomy_dict
    let raw_group_prob_dict = raw_data.group_prob_dict
    let ctx = document.getElementById('myChart');
    let select = document.getElementById('selectClassifier')

    //checkear
    reverseData(raw_tax)

    probability_data_aux = []
    mychart = new Chart(ctx, config);

    select.addEventListener('change', (e) => {
        updateMyChart(e.target.value, raw_tax, raw_group_prob_dict)
    })
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

function updateMyChart(classifier_name, raw_tax, raw_group_prob_dict){
    let max_value
    let classes_arr = raw_tax[classifier_name].classes
    let classifier_data = Object.values(raw_group_prob_dict[classifier_name])[0]

    orderDataByTagNew(classes_arr, classifier_data)

    max_value = maxValue(classifier_data)

    removeDataChart()
    updateDataChart(classes_arr, max_value)

    isDark();
}

function removeDataChart(){
    mychart.data.labels.length = 0;
    mychart.data.datasets.forEach((dataset) => {
        dataset.data.length = 0;

    });

    mychart.update();
}

function updateDataChart(labels, max_value){
    mychart.data.labels.push(...labels);
    mychart.data.datasets.forEach((dataset) => {
        dataset.data.push(...probability_data_aux);
    });

    mychart.config.options.scales.r.ticks.stepSize = getScale(max_value)
    mychart.config.options.scales.r.max = max_value

    mychart.update();
}

function isDark(){
    if(document.getElementById("probabilities-app").classList.contains("tw-dark")){
        mychart.config.options.scales.r.backgroundColor = '#BDBDBD'
        mychart.config.options.scales.r.angleLines.color = '#EEEEEE'
        mychart.config.options.scales.r.grid.color = '#EEEEEE'
        mychart.config.options.scales.r.pointLabels.color = '#EEEEEE'
        
        mychart.update();
    }
}